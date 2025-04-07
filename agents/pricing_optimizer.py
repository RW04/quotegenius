# agents/pricing_optimizer.py
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from typing import Dict, Any, List
import logging
import os
import json

class PricingOptimizerAgent:
    """
    Specialized agent responsible for optimizing quote pricing
    to maximize win probability while maintaining desired margins.
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
        
        # Initialize optimization prompt template
        self.optimization_prompt = ChatPromptTemplate.from_template("""
            You are an expert manufacturing pricing strategist with years of experience.
            
            ## Quote Details
            {quote_details}
            
            ## Similar Projects Pricing
            {similar_projects_pricing}
            
            ## Customer Information
            {customer_info}
            
            ## Market Conditions
            Current market conditions suggest materials costs are {market_trend} and competition is {competition_level}.
            
            ## Optimization Task
            Optimize the pricing in this quote to maximize our win probability while maintaining healthy margins.
            
            Consider:
            1. The customer's history and relationship with us
            2. Competitive positioning in the market
            3. Project complexity and risk factors
            4. Cost structure and potential for efficiency
            5. Strategic value of winning this project
            
            Provide:
            1. Recommended adjustments to specific line items
            2. Overall pricing strategy recommendation
            3. Justification for your recommendations
            4. Expected impact on win probability and profit margin
            
            Format your response as JSON with clear recommendations and rationale.
        """)
        
        # Create the optimization chain
        self.optimization_chain = LLMChain(llm=self.llm, prompt=self.optimization_prompt)
        
    def optimize_pricing(self, quote_data: Dict[str, Any], similar_projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Optimize the pricing of a quote based on historical data and market conditions.
        """
        self.logger.info(f"Optimizing pricing for quote: {quote_data.get('quote_id', 'new quote')}")
        
        # Extract customer information if available
        customer_info = self._get_customer_info(quote_data.get("customer_id"))
        
        # Format similar projects pricing data
        similar_projects_pricing = self._format_similar_projects(similar_projects)
        
        # Generate current market conditions assessment
        # In a real implementation, this would come from external data sources
        market_conditions = self._assess_market_conditions()
        
        # Execute the LLM chain to optimize pricing
        optimization_result = self.optimization_chain.run(
            quote_details=json.dumps(quote_data, indent=2),
            similar_projects_pricing=similar_projects_pricing,
            customer_info=json.dumps(customer_info, indent=2) if customer_info else "No customer history available",
            market_trend=market_conditions["materials_trend"],
            competition_level=market_conditions["competition_level"]
        )
        
        # Process the optimization result
        try:
            optimization_recommendations = json.loads(optimization_result)
        except json.JSONDecodeError:
            self.logger.error("Failed to parse optimization result as JSON")
            optimization_recommendations = {
                "raw_recommendations": optimization_result,
                "error": "Failed to structure recommendations properly"
            }
        
        # Apply the optimizations to the quote
        optimized_quote = self._apply_optimizations(quote_data, optimization_recommendations)
        
        return optimized_quote
    
    def deep_optimize(self, quote_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a deeper optimization analysis on an existing quote.
        """
        self.logger.info(f"Performing deep optimization for quote: {quote_data.get('quote_id')}")
        
        # Find similar projects that have been successful
        similar_successful_projects = self._find_successful_similar_projects(quote_data)
        
        # Run the standard optimization with focused data
        return self.optimize_pricing(quote_data, similar_successful_projects)
    
    def update_models_with_feedback(self, feedback_data: Dict[str, Any]) -> None:
        """
        Update optimization models based on quote feedback.
        In a production system, this would update ML models or heuristics.
        """
        self.logger.info(f"Updating models with feedback for quote: {feedback_data['quote_id']}")
        
        # In a real implementation, this would update ML models or parameters
        # For this POC, we'll just log that it happened
        self.logger.info(f"Feedback processed: Quote was {'accepted' if feedback_data['accepted'] else 'rejected'}")
        
    def _get_customer_info(self, customer_id: str) -> Dict[str, Any]:
        """
        Retrieve customer information and quote history.
        """
        if not customer_id:
            return {}
        
        # Get basic customer data
        customer_data = self.structured_db.get_customer_data(customer_id)
        if not customer_data:
            return {}
        
        # Get customer's quote history
        quote_history = self.structured_db.get_customer_quotes(customer_id)
        
        # Calculate customer metrics
        if quote_history:
            # Calculate win rate
            statuses = [q.get("status", "pending") for q in quote_history]
            win_rate = statuses.count("accepted") / len(statuses) if statuses else 0
            
            # Calculate average project size
            avg_project_size = sum(q.get("total_price", 0) for q in quote_history) / len(quote_history)
            
            customer_data["win_rate"] = win_rate
            customer_data["avg_project_size"] = avg_project_size
            customer_data["total_projects"] = len(quote_history)
        
        return customer_data
    
    def _format_similar_projects(self, similar_projects: List[Dict[str, Any]]) -> str:
        """
        Format similar projects data for the LLM prompt.
        """
        if not similar_projects:
            return "No similar projects found in our database."
        
        formatted_data = []
        for idx, project in enumerate(similar_projects, 1):
            project_info = f"Project {idx}: {project.get('project_name', 'Unnamed')}\n"
            project_info += f"  - Total Price: ${project.get('total_price', 0):,.2f}\n"
            project_info += f"  - Status: {project.get('status', 'unknown')}\n"
            
            if "breakdown" in project:
                project_info += "  - Cost Breakdown:\n"
                for category, amount in project["breakdown"].items():
                    project_info += f"    * {category.capitalize()}: ${amount:,.2f}\n"
            
            formatted_data.append(project_info)
        
        return "\n".join(formatted_data)
    
    def _assess_market_conditions(self) -> Dict[str, str]:
        """
        Assess current market conditions affecting pricing decisions.
        In a real implementation, this would use external data sources.
        """
        # For demo purposes, we'll use static conditions
        # In a real implementation, this would connect to market data APIs
        return {
            "materials_trend": "increasing moderately",
            "competition_level": "highly competitive",
            "labor_market": "tight",
            "economic_outlook": "stable"
        }
    
    def _apply_optimizations(self, quote_data: Dict[str, Any], recommendations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply optimization recommendations to the quote.
        """
        # Create a copy of the original quote to avoid modifying it
        optimized_quote = dict(quote_data)
        
        # Apply line item adjustments if provided
        if "line_item_adjustments" in recommendations:
            if "breakdown" not in optimized_quote:
                optimized_quote["breakdown"] = {}
                
            for item, adjustment in recommendations["line_item_adjustments"].items():
                if item in optimized_quote["breakdown"]:
                    # Update existing breakdown item
                    if isinstance(adjustment, dict) and "value" in adjustment:
                        optimized_quote["breakdown"][item] = adjustment["value"]
                    elif isinstance(adjustment, (int, float)):
                        optimized_quote["breakdown"][item] = adjustment
                else:
                    # Add new breakdown item
                    if isinstance(adjustment, dict) and "value" in adjustment:
                        optimized_quote["breakdown"][item] = adjustment["value"]
                    elif isinstance(adjustment, (int, float)):
                        optimized_quote["breakdown"][item] = adjustment
        
        # Update total price if provided
        if "recommended_total_price" in recommendations:
            optimized_quote["total_price"] = recommendations["recommended_total_price"]
            
        # Otherwise recalculate total from breakdown
        elif "breakdown" in optimized_quote:
            optimized_quote["total_price"] = sum(optimized_quote["breakdown"].values())
        
        # Add optimization metadata
        optimized_quote["optimization"] = {
            "recommendations": recommendations,
            "original_price": quote_data.get("total_price"),
            "price_change_percentage": ((optimized_quote["total_price"] - quote_data.get("total_price", 0)) / 
                                        quote_data.get("total_price", 1)) * 100 if "total_price" in quote_data else 0
        }
        
        return optimized_quote
    
    def _find_successful_similar_projects(self, quote_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find similar projects that were successfully won.
        """
        # This would normally use more sophisticated similarity search
        # For demo purposes, we'll simulate this with structured DB queries
        
        # Get projects in the same price range
        price_min = quote_data.get("total_price", 0) * 0.8
        price_max = quote_data.get("total_price", 0) * 1.2
        
        try:
            conn = self.structured_db.db_path
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT quote_data
                FROM quotes
                WHERE total_price BETWEEN ? AND ?
                AND status = 'accepted'
                ORDER BY timestamp DESC
                LIMIT 5
                """,
                (price_min, price_max)
            )
            
            results = cursor.fetchall()
            conn.close()
            
            return [json.loads(row[0]) for row in results]
        except Exception as e:
            self.logger.error(f"Error finding successful projects: {str(e)}")
            return []