# agents/coordinator.py
from crewai import Agent, Task, Crew, Process
from langchain.chat_models import ChatOpenAI
from typing import Dict, Any, List
import logging
import os

class CoordinatorAgent:
    """
    Coordinator Agent that orchestrates the entire quote generation process.
    Acts as the central system that delegates tasks to specialized agents.
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo",
            temperature=0.2,
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        self.agents = {}
        self.logger = logging.getLogger(__name__)
        
    def register_agents(self, **agents):
        """Register all specialized agents with the coordinator."""
        self.agents = agents
        self.logger.info(f"Registered {len(agents)} specialized agents")
        
    def process_quote_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a new quote request by coordinating between various agents.
        """
        self.logger.info(f"Processing quote request: {request_data['project_name']}")
        
        # Step 1: Have data analyst agent analyze project requirements
        project_analysis = self.agents['data_analyst'].analyze_project_requirements(request_data)
        
        # Step 2: Check for similar past projects in the database
        similar_projects = self.agents['data_analyst'].find_similar_projects(request_data)
        
        # Step 3: Get relevant business rules and constraints
        business_rules = self.agents['knowledge_agent'].get_business_rules(request_data['customer_id'])
        
        # Step 4: Generate the initial quote
        quote_data = self.agents['quote_generator'].generate_quote(
            request_data,
            project_analysis,
            similar_projects,
            business_rules
        )
        
        # Step 5: Optimize pricing strategy
        optimized_quote = self.agents['pricing_optimizer'].optimize_pricing(
            quote_data,
            similar_projects
        )
        
        # Step 6: Generate explanations and recommendations
        recommendations = self.agents['knowledge_agent'].generate_recommendations(optimized_quote)
        
        # Compile final response
        final_response = {
            "quote_id": optimized_quote["quote_id"],
            "customer_id": request_data["customer_id"],
            "project_name": request_data["project_name"],
            "total_price": optimized_quote["total_price"],
            "breakdown": optimized_quote["breakdown"],
            "confidence_score": optimized_quote["confidence_score"],
            "recommendations": recommendations,
            "generated_at": optimized_quote["timestamp"]
        }
        
        self.logger.info(f"Quote generated successfully: {final_response['quote_id']}")
        return final_response
    
    def optimize_quote(self, quote_id: str) -> Dict[str, Any]:
        """
        Further optimize an existing quote based on additional context or constraints.
        """
        # Get existing quote data
        quote_data = self.agents['data_analyst'].get_quote(quote_id)
        if not quote_data:
            raise ValueError(f"Quote with ID {quote_id} not found")
        
        # Run deeper optimization
        optimized_quote = self.agents['pricing_optimizer'].deep_optimize(quote_data)
        
        # Update recommendations
        recommendations = self.agents['knowledge_agent'].generate_recommendations(optimized_quote)
        
        # Return optimized quote
        optimized_quote["recommendations"] = recommendations
        
        return optimized_quote
    
    def process_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process feedback on quotes to improve future quote generation.
        """
        # Record feedback in structured database
        self.agents['data_analyst'].record_feedback(
            feedback_data["quote_id"], 
            feedback_data["feedback"],
            feedback_data["accepted"]
        )
        
        # Update optimization models based on new feedback
        self.agents['pricing_optimizer'].update_models_with_feedback(feedback_data)
        
        # Return success message
        return {
            "status": "success",
            "message": "Feedback processed successfully",
            "quote_id": feedback_data["quote_id"]
        }

    def run_crew_ai_workflow(self, request_data):
        """
        Alternative implementation using CrewAI's structured workflow approach.
        This demonstrates how to use the CrewAI framework for larger agent systems.
        """
        # Define agents for CrewAI
        analyst = Agent(
            role="Data Analyst",
            goal="Analyze project requirements and find patterns in historical data",
            backstory="Expert in analyzing manufacturing data to uncover insights",
            verbose=True,
            llm=self.llm
        )
        
        quote_expert = Agent(
            role="Quote Generation Expert",
            goal="Generate accurate and competitive quotes",
            backstory="Specialist in creating detailed and precise manufacturing quotes",
            verbose=True,
            llm=self.llm
        )
        
        pricing_expert = Agent(
            role="Pricing Optimization Expert", 
            goal="Optimize quote pricing for maximum profitability while remaining competitive",
            backstory="Expert in balancing profit margins with market competitiveness",
            verbose=True,
            llm=self.llm
        )
        
        # Define tasks
        analyze_task = Task(
            description=f"Analyze the following project requirements: {request_data['project_description']}",
            agent=analyst,
            expected_output="Detailed analysis of project requirements and potential challenges"
        )
        
        quote_task = Task(
            description="Generate a detailed quote based on the project analysis",
            agent=quote_expert,
            expected_output="Complete quote with line-item breakdowns",
            context=[analyze_task]
        )
        
        optimize_task = Task(
            description="Optimize the quote pricing for maximum profitability",
            agent=pricing_expert,
            expected_output="Optimized quote with pricing recommendations",
            context=[quote_task]
        )
        
        # Create crew with sequential process
        crew = Crew(
            agents=[analyst, quote_expert, pricing_expert],
            tasks=[analyze_task, quote_task, optimize_task],
            verbose=True,
            process=Process.sequential
        )
        
        # Execute the crew workflow
        result = crew.kickoff()
        return result