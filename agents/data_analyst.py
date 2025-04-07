# agents/data_analyst.py
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from typing import Dict, Any, List, Optional
import logging
import os

class DataAnalystAgent:
    """
    Specialized agent responsible for analyzing data, finding patterns,
    and extracting insights from historical quotes and project data.
    """
    
    def __init__(self, vector_db, structured_db):
        self.vector_db = vector_db
        self.structured_db = structured_db
        self.llm = ChatOpenAI(
            model="gpt-4-turbo",
            temperature=0.2,
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize analysis prompt template
        self.analysis_prompt = ChatPromptTemplate.from_template("""
            You are an expert data analyst specializing in manufacturing projects and quotes.
            
            ## Project Details
            Project Name: {project_name}
            Description: {project_description}
            Materials Required: {materials}
            Labor Hours (estimated): {labor_hours}
            Deadline: {deadline}
            Special Requirements: {special_requirements}
            
            ## Task
            Analyze this project information and provide insights that would be valuable 
            for generating an accurate manufacturing quote. Consider:
            
            1. Potential complexity factors that might impact cost
            2. Risks that should be accounted for in pricing
            3. Material considerations (availability, price volatility, etc.)
            4. Labor intensity and specialized skills required
            5. Timeline feasibility and potential bottlenecks
            
            Format your analysis as a structured JSON with clear sections for each area.
        """)
        
        # Create the analysis chain
        self.analysis_chain = LLMChain(llm=self.llm, prompt=self.analysis_prompt)
        
    def analyze_project_requirements(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze project requirements to identify key factors affecting the quote.
        """
        self.logger.info(f"Analyzing project requirements for: {request_data['project_name']}")
        
        # Execute the LLM chain to analyze the project
        analysis_result = self.analysis_chain.run(
            project_name=request_data["project_name"],
            project_description=request_data["project_description"],
            materials=request_data["materials"],
            labor_hours=request_data.get("labor_hours", "Not specified"),
            deadline=request_data.get("deadline", "Not specified"),
            special_requirements=request_data.get("special_requirements", "None")
        )
        
        # Process and structure the analysis result
        try:
            import json
            structured_analysis = json.loads(analysis_result)
        except json.JSONDecodeError:
            self.logger.error("Failed to parse analysis result as JSON")
            # Fallback with raw text
            structured_analysis = {
                "raw_analysis": analysis_result,
                "error": "Failed to structure analysis properly"
            }
        
        return structured_analysis
    
    def find_similar_projects(self, request_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find historical projects similar to the current request.
        """
        self.logger.info(f"Finding similar projects for: {request_data['project_name']}")
        
        # Use the project description to search for similar projects
        project_description = request_data["project_description"]
        similar_projects = self.vector_db.search_similar_projects(project_description)
        
        # If we have a customer ID, also check the structured DB for this customer's past quotes
        if "customer_id" in request_data:
            customer_quotes = self.structured_db.get_customer_quotes(request_data["customer_id"])
            
            # Merge results, removing duplicates
            existing_ids = {p.get("project_id") for p in similar_projects}
            for quote in customer_quotes:
                if quote.get("quote_id") not in existing_ids:
                    similar_projects.append(quote)
                    existing_ids.add(quote.get("quote_id"))
        
        return similar_projects[:10]  # Limit to top 10 most relevant
    
    def get_quote(self, quote_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a quote by ID from the database.
        """
        return self.structured_db.get_quote(quote_id)
    
    def record_feedback(self, quote_id: str, feedback: str, accepted: bool) -> bool:
        """
        Record customer feedback on a quote.
        """
        return self.structured_db.record_feedback(quote_id, feedback, accepted)
    
    def get_market_insights(self) -> Dict[str, Any]:
        """
        Generate market insights based on historical quote data.
        """
        self.logger.info("Generating market insights")
        
        # Get analytics data from structured database
        analytics_data = self.structured_db.get_quote_analytics()
        
        # Use LLM to generate insights from the analytics
        insights_prompt = ChatPromptTemplate.from_template("""
            You are an expert data analyst specializing in manufacturing quoting trends.
            
            Analyze the following analytics data from our quote database:
            
            {analytics_data}
            
            Based on this data, provide strategic insights about:
            
            1. Win rate trends and potential factors affecting them
            2. Pricing strategies that seem most effective
            3. Industry or customer segments that show the most promising opportunities
            4. Recommendations for optimizing our quoting process
            
            Format your insights as a concise, actionable report with clear recommendations.
        """)
        
        insights_chain = LLMChain(llm=self.llm, prompt=insights_prompt)
        
        insights_text = insights_chain.run(analytics_data=str(analytics_data))
        
        # Combine raw analytics with generated insights
        return {
            "raw_analytics": analytics_data,
            "insights": insights_text
        }