# agents/quote_generator.py
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from typing import Dict, Any, List
import uuid
from datetime import datetime
import logging
import os

class QuoteGeneratorAgent:
    """
    Specialized agent responsible for generating detailed manufacturing quotes
    based on project requirements, historical data, and business rules.
    """
    
    def __init__(self, vector_db, structured_db):
        self.vector_db = vector_db
        self.structured_db = structured_db
        self.llm = ChatOpenAI(
            model="gpt-4-turbo",
            temperature=0.1,
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize quote generation prompt template
        self.quote_prompt = ChatPromptTemplate.from_template("""
            You are an expert manufacturing quote generator with years of experience.
            
            ## Project Details
            Customer: {customer_id}
            Project Name: {project_name}
            Description: {project_description}
            Materials Required: {materials}
            Labor Hours (estimated): {labor_hours}
            Deadline: {deadline}
            Special Requirements: {special_requirements}
            
            ## Historical Data Insights
            Similar Projects Analysis: {similar_projects_analysis}
            
            ## Business Rules
            Customer-Specific Rules: {business_rules}
            
            ## Instructions
            Generate a detailed manufacturing quote with the following:
            1. Line-item breakdown of all materials with quantities and unit prices
            2. Labor costs with hourly rates and estimated hours
            3. Equipment/machinery costs
            4. Overhead percentage
            5. Profit margin (consider customer relationship, project complexity, and market conditions)
            6. Any discounts or special pricing considerations
            7. Timeline for delivery with key milestones
            8. Terms and conditions summary
            
            Format your response as a structured JSON object that can be easily processed.
            Include a confidence score (0-100) for your quote based on the quality of available information.
        """)
        
        # Create the chain
        self.quote_chain = LLMChain(llm=self.llm, prompt=self.quote_prompt)
        
    def generate_quote(self, 
                       request_data: Dict[str, Any], 
                       project_analysis: Dict[str, Any],
                       similar_projects: List[Dict[str, Any]],
                       business_rules: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive quote based on project requirements and analysis.
        """
        self.logger.info(f"Generating quote for project: {request_data['project_name']}")
        
        # Prepare similar projects analysis summary
        similar_projects_summary = self._summarize_similar_projects(similar_projects)
        
        # Execute the LLM chain to generate the quote
        quote_result = self.quote_chain.run(
            customer_id=request_data["customer_id"],
            project_name=request_data["project_name"],
            project_description=request_data["project_description"],
            materials=request_data["materials"],
            labor_hours=request_data.get("labor_hours", "Not specified"),
            deadline=request_data.get("deadline", "Not specified"),
            special_requirements=request_data.get("special_requirements", "None"),
            similar_projects_analysis=similar_projects_summary,
            business_rules=business_rules
        )
        
        # Process and structure the quote result (assuming the LLM returns JSON-formatted string)
        try:
            import json
            structured_quote = json.loads(quote_result)
        except json.JSONDecodeError:
            self.logger.error("Failed to parse quote result as JSON")
            # Fallback to raw result with minimal structure
            structured_quote = {
                "raw_quote": quote_result,
                "error": "Failed to structure quote properly"
            }
        
        # Add metadata
        quote_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        final_quote = {
            "quote_id": quote_id,
            "timestamp": timestamp,
            "customer_id": request_data["customer_id"],
            "project_name": request_data["project_name"],
            **structured_quote
        }
        
        # Store the quote in the database
        self._store_quote(final_quote)
        
        return final_quote
    
    def _summarize_similar_projects(self, similar_projects: List[Dict[str, Any]]) -> str:
        """
        Summarize insights from similar projects to inform the quote generation.
        """
        if not similar_projects:
            return "No similar projects found in historical data."
        
        # Use LLM to generate a concise summary of similar projects
        summary_prompt = ChatPromptTemplate.from_template("""
            Analyze the following historical projects similar to the current project:
            
            {similar_projects}
            
            Provide a concise summary of insights that would be relevant for generating 
            a new quote, including:
            - Average cost ranges for materials and labor
            - Common challenges and how they affected pricing
            - Typical profit margins applied
            - Any patterns in customer satisfaction or project outcomes
            
            Format as a concise bulleted list of key insights.
        """)
        
        summary_chain = LLMChain(llm=self.llm, prompt=summary_prompt)
        
        # Convert similar projects to a string representation
        projects_str = "\n\n".join([
            f"Project: {p.get('project_name')}\n"
            f"Final Cost: ${p.get('total_price')}\n"
            f"Profit Margin: {p.get('profit_margin')}%\n"
            f"Customer Satisfied: {p.get('customer_satisfied', 'Unknown')}\n"
            f"Key Challenges: {p.get('challenges', 'None recorded')}"
            for p in similar_projects
        ])
        
        summary = summary_chain.run(similar_projects=projects_str)
        return summary
    
    def _store_quote(self, quote_data: Dict[str, Any]) -> None:
        """
        Store the generated quote in the database for future reference.
        """
        try:
            self.structured_db.store_quote(quote_data)
            self.logger.info(f"Quote {quote_data['quote_id']} stored successfully")
        except Exception as e:
            self.logger.error(f"Failed to store quote: {str(e)}")
            # Continue execution - this is non-critical
            pass