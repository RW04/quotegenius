# db/vector_store.py
import os
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
import logging
from typing import List, Dict, Any

class VectorStore:
    """
    Vector database for semantic search and retrieval of past quotes,
    project information, and business rules.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Initialize embeddings model
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        
        # Create collections for different types of data
        self.quotes_db = self._initialize_collection("quotes")
        self.projects_db = self._initialize_collection("projects")
        self.rules_db = self._initialize_collection("business_rules")
        
        # If running for the first time, seed with synthetic data
        if os.environ.get("SEED_DB", "false").lower() == "true":
            self._seed_database()
    
    def _initialize_collection(self, collection_name: str):
        """Initialize a Chroma collection for vector storage."""
        try:
            persist_directory = f"./data/vector_db/{collection_name}"
            os.makedirs(persist_directory, exist_ok=True)
            
            return Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=persist_directory
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize {collection_name} collection: {str(e)}")
            # Return a simple in-memory collection as fallback
            return Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings
            )
    
    def search_similar_projects(self, project_description: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar past projects based on project description.
        """
        try:
            results = self.projects_db.similarity_search_with_score(
                project_description, 
                k=k
            )
            
            # Extract and format the results
            similar_projects = []
            for doc, score in results:
                project_data = doc.metadata
                project_data["similarity_score"] = score
                project_data["description"] = doc.page_content
                similar_projects.append(project_data)
                
            return similar_projects
        except Exception as e:
            self.logger.error(f"Error searching similar projects: {str(e)}")
            return []
    
    def get_business_rules(self, customer_id: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve business rules relevant to a specific customer or general rules.
        """
        try:
            # Search for customer-specific rules first
            query = f"Business rules for customer {customer_id}"
            if customer_id:
                results = self.rules_db.similarity_search_with_score(
                    query,
                    k=10,
                    filter={"customer_id": customer_id}
                )
            
            # Add general rules
            general_results = self.rules_db.similarity_search_with_score(
                "General business rules for quoting",
                k=5,
                filter={"rule_type": "general"}
            )
            
            # Combine and format results
            all_results = results + general_results if customer_id else general_results
            
            # Extract and format the rules
            business_rules = []
            for doc, score in all_results:
                rule_data = doc.metadata
                rule_data["rule_description"] = doc.page_content
                rule_data["relevance_score"] = score
                business_rules.append(rule_data)
                
            return business_rules
        except Exception as e:
            self.logger.error(f"Error retrieving business rules: {str(e)}")
            return []
    
    def add_project(self, project_data: Dict[str, Any]) -> bool:
        """
        Add a new project to the vector database.
        """
        try:
            # Extract the description as the main content
            description = project_data.get("project_description", "")
            
            # Add the document with metadata
            self.projects_db.add_texts(
                texts=[description],
                metadatas=[project_data]
            )
            
            # Persist the changes
            self.projects_db.persist()
            return True
        except Exception as e:
            self.logger.error(f"Error adding project to vector DB: {str(e)}")
            return False
    
    def _seed_database(self):
        """Seed the database with synthetic data for demo purposes."""
        # Add sample projects
        sample_projects = [
            {
                "project_id": "proj-001",
                "customer_id": "cust-101",
                "project_name": "Industrial Valve Assembly",
                "project_description": "Manufacturing of 500 custom industrial valves for high-pressure systems.",
                "total_price": 125000.00,
                "profit_margin": 22.5,
                "customer_satisfied": True,
                "completion_date": "2023-05-15"
            },
            {
                "project_id": "proj-002",
                "customer_id": "cust-102",
                "project_name": "Aerospace Component Fabrication",
                "project_description": "Precision machining of titanium components for aerospace applications.",
                "total_price": 287500.00,
                "profit_margin": 18.3,
                "customer_satisfied": True,
                "completion_date": "2023-07-22"
            },
            {
                "project_id": "proj-003",
                "customer_id": "cust-101",
                "project_name": "Hydraulic System Overhaul",
                "project_description": "Complete redesign and manufacturing of hydraulic control systems.",
                "total_price": 195000.00,
                "profit_margin": 24.1,
                "customer_satisfied": False,
                "challenges": "Material delays, design changes mid-project"
            }
        ]
        
        for project in sample_projects:
            self.add_project(project)
        
        # Add business rules
        sample_rules = [
            {
                "rule_id": "rule-001",
                "rule_type": "general",
                "rule_description": "Standard markup for raw materials is 15-20% depending on market volatility."
            },
            {
                "rule_id": "rule-002",
                "rule_type": "general",
                "rule_description": "Labor rates must include 25% overhead for benefits and facility costs."
            },
            {
                "rule_id": "rule-003",
                "customer_id": "cust-101",
                "rule_type": "customer-specific",
                "rule_description": "Customer 101 has negotiated a 5% volume discount on orders over $100,000."
            }
        ]
        
        for rule in sample_rules:
            self.rules_db.add_texts(
                texts=[rule["rule_description"]],
                metadatas=[rule]
            )
        
        # Persist all changes
        self.rules_db.persist()
        self.logger.info("Database seeded with sample data")