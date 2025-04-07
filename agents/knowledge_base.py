# agents/knowledge_base.py
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from typing import Dict, Any, List
import logging
import os

class KnowledgeBaseAgent:
    """
    Specialized agent that maintains business rules, industry knowledge,
    and generates recommendations based on domain expertise.
    """
    
    def __init__(self, vector_db):
        self.vector_db = vector_db
        self.llm = ChatOpenAI(
            model="gpt-4-turbo",
            temperature=0.2,
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize recommendation prompt template
        self.recommendation_prompt = ChatPromptTemplate.from_template("""
            You are an expert manufacturing consultant with extensive industry knowledge.
            
            ## Quote Details
            {quote_details}
            
            ## Task
            Based on this manufacturing quote, provide strategic recommendations to:
            
            1. Increase the likelihood of winning the project
            2. Identify potential cost-saving opportunities
            3. Highlight risk factors that may require mitigation
            4. Suggest value-added services that could enhance the proposal
            
            Format your recommendations as concise, actionable bullet points that
            a manufacturing company could use when discussing this quote with the client.
        """)
        
        # Create the recommendation chain
        self.recommendation_chain = LLMChain(llm=self.llm, prompt=self.recommendation_prompt)
        
    def get_business_rules(self, customer_id: str = None) -> Dict[str, Any]:
        """
        Retrieve relevant business rules for quoting based on customer and project type.
        """
        self.logger.info(f"Retrieving business rules for customer: {customer_id}")
        
        # Get rules from vector DB
        rules = self.vector_db.get_business_rules(customer_id)
        
        # Format rules into structured output
        rules_by_category = {}
        
        for rule in rules:
            category = rule.get("rule_type", "general")
            
            if category not in rules_by_category:
                rules_by_category[category] = []
                
            rules_by_category[category].append({
                "rule_id": rule.get("rule_id", "unknown"),
                "description": rule.get("rule_description", ""),
                "relevance_score": rule.get("relevance_score", 1.0)
            })
        
        # Add default rules if no rules found
        if not rules_by_category:
            rules_by_category["general"] = [
                {
                    "rule_id": "default-1",
                    "description": "Standard markup for materials is 15%",
                    "relevance_score": 1.0
                },
                {
                    "rule_id": "default-2",
                    "description": "Apply 25% overhead rate to labor costs",
                    "relevance_score": 1.0
                },
                {
                    "rule_id": "default-3",
                    "description": "Add 10% contingency for complex projects",
                    "relevance_score": 1.0
                }
            ]
        
        return rules_by_category
    
    def generate_recommendations(self, quote_data: Dict[str, Any]) -> List[str]:
        """
        Generate strategic recommendations based on quote details.
        """
        self.logger.info(f"Generating recommendations for quote: {quote_data.get('quote_id', 'new quote')}")
        
        # Format quote data for the prompt
        import json
        quote_details = json.dumps(quote_data, indent=2)
        
        # Execute the recommendation chain
        recommendations_text = self.recommendation_chain.run(quote_details=quote_details)
        
        # Process the recommendations into a list
        recommendations_list = self._process_recommendations(recommendations_text)
        
        return recommendations_list
    
    def _process_recommendations(self, recommendations_text: str) -> List[str]:
        """
        Process raw recommendations text into a structured list.
        """
        # Split the text by lines and clean up bullet points
        lines = recommendations_text.strip().split("\n")
        
        # Filter empty lines and cleanup bullet point formats
        processed_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Remove common bullet point markers
            for marker in ["- ", "* ", "• ", "· ", "1. ", "2. ", "3. ", "4. ", "5. "]:
                if line.startswith(marker):
                    line = line[len(marker):]
                    break
                    
            processed_lines.append(line)
        
        return processed_lines