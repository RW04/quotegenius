# app.py
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
from datetime import datetime
import json

# Import agent system
from agents.coordinator import CoordinatorAgent
from agents.data_analyst import DataAnalystAgent
from agents.quote_generator import QuoteGeneratorAgent
from agents.pricing_optimizer import PricingOptimizerAgent
from agents.knowledge_base import KnowledgeBaseAgent

# Import database connections
from db.vector_store import VectorStore
from db.structured_db import StructuredDB

app = FastAPI(title="QuoteGenius API", description="AI-powered manufacturing quote system")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize databases
vector_db = VectorStore()
structured_db = StructuredDB()

# Initialize agents
coordinator = CoordinatorAgent()
data_analyst = DataAnalystAgent(vector_db, structured_db)
quote_generator = QuoteGeneratorAgent(vector_db, structured_db)
pricing_optimizer = PricingOptimizerAgent(vector_db, structured_db)
knowledge_agent = KnowledgeBaseAgent(vector_db)

# Connect agents to coordinator
coordinator.register_agents(
    data_analyst=data_analyst,
    quote_generator=quote_generator,
    pricing_optimizer=pricing_optimizer,
    knowledge_agent=knowledge_agent
)

# Define request models
class QuoteRequest(BaseModel):
    customer_id: str
    project_name: str
    project_description: str
    materials: List[Dict[str, Any]]
    labor_hours: Optional[float] = None
    deadline: Optional[str] = None
    special_requirements: Optional[str] = None

class FeedbackRequest(BaseModel):
    quote_id: str
    feedback: str
    accepted: bool

# API Routes
@app.get("/")
async def root():
    return {"message": "Welcome to QuoteGenius API"}

@app.post("/generate-quote")
async def generate_quote(request: QuoteRequest):
    try:
        # Process the quote request through the coordinator agent
        quote_result = coordinator.process_quote_request(request.dict())
        return quote_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize-quote/{quote_id}")
async def optimize_quote(quote_id: str):
    try:
        optimization_result = coordinator.optimize_quote(quote_id)
        return optimization_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/quote-feedback")
async def submit_feedback(feedback: FeedbackRequest):
    try:
        # Process feedback through coordinator to improve future quotes
        feedback_result = coordinator.process_feedback(feedback.dict())
        return feedback_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market-insights")
async def get_market_insights():
    try:
        insights = data_analyst.get_market_insights()
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)