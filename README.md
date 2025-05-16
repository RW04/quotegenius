# QuoteGenius

AI-powered manufacturing quote system that uses intelligent agents to generate accurate, competitive quotes. This project demonstrates a multi-agent LLM architecture for optimizing quoting processes in manufacturing.

![Architecture Diagram](static/architecture-diagram.md)

## Features

- **Multi-Agent AI System** utilizing specialized agents for different aspects of quote generation
- **Interactive Dashboard** with performance metrics and visualization
- **Quote Generation** with AI-powered pricing strategy and recommendations
- **Market Insights** for data-driven business decisions
- **Semantic Search** to find similar historical projects

## Architecture

QuoteGenius uses a collaborative agent architecture:

- **Coordinator Agent**: Orchestrates the entire quote generation process
- **Data Analyst Agent**: Analyzes project requirements and historical data
- **Quote Generator Agent**: Creates detailed quotes with line-item breakdown
- **Pricing Optimizer Agent**: Maximizes win probability while maintaining margins
- **Knowledge Base Agent**: Applies business rules and domain expertise

The system leverages vector databases for semantic similarity and structured databases for relational data storage.

## Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API key

### Installation

1. Clone the repository

```python
git clone https://github.com/your-username/QuoteGenius.git
cd QuoteGenius
```

2. Create a virtual environment

```python
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```python

pip install -r requirements.txt
```

4. Create a `.env` file with your OpenAI API key

```python
OPENAI_API_KEY=your_api_key_here
```

### Running the Application

Run the application with the following command:

```python
python run.py
```

For demo mode only (no backend required):

```python
python run.py --ui-only
```

## Usage Guide

### Dashboard

The dashboard provides an overview of quoting performance with metrics including:

- Total quotes year-to-date
- Win rate with trend
- Average quote value
- Response time statistics

### Generating a Quote

1. Navigate to the "Generate Quote" page
2. Select a customer or add a new one
3. Enter project details and material requirements
4. Click "Generate Quote" to start the AI process
5. Review the generated quote with pricing breakdown
6. Optionally click "Optimize Quote" for AI-driven price optimization

### Market Insights

Explore data-driven insights including:

- Price trends by industry
- Win rate analysis by response time and quote value
- Customer portfolio visualization
- Material cost trends and forecasts

## Technical Documentation

### System Components

#### Agent System

The multi-agent system consists of:

1. **Coordinator Agent** (`agents/coordinator.py`):
   - Manages workflow between specialized agents
   - Delegates tasks and aggregates results
   - Provides a unified interface to the API layer

2. **Data Analyst Agent** (`agents/data_analyst.py`):
   - Analyzes project requirements
   - Retrieves and analyzes historical data
   - Identifies patterns and insights

3. **Quote Generator Agent** (`agents/quote_generator.py`):
   - Creates detailed quotes with line-item breakdown
   - Applies business rules to pricing
   - Generates comprehensive documentation

4. **Pricing Optimizer Agent** (`agents/pricing_optimizer.py`):
   - Optimizes pricing strategy for maximum win probability
   - Balances competitiveness with profitability
   - Incorporates market conditions and customer relationship

5. **Knowledge Base Agent** (`agents/knowledge_base.py`):
   - Manages domain-specific knowledge
   - Applies business rules and policies
   - Generates strategic recommendations

#### Data Layer

1. **Vector Database** (`db/vector_store.py`):
   - Stores embeddings for semantic search capabilities
   - Enables similarity matching for projects and rules
   - Implemented using Chroma vector database

2. **Structured Database** (`db/structured_db.py`):
   - Stores relational data (quotes, customers, feedback)
   - Tracks quote history and performance
   - Implemented using SQLite

#### User Interface

The Streamlit-based UI (`app_ui.py`) provides:

- Interactive dashboard with performance metrics
- Quote generation interface with dynamic forms
- Visualization of quote breakdown and recommendations
- Historical data analysis and filtering

#### API Layer

The FastAPI backend (`app.py`) provides:

- RESTful endpoints for quote generation and retrieval
- Integration with the agent system
- Data validation and error handling

### Data Flow

1. User submits a quote request through the UI
2. Request is sent to the API layer
3. Coordinator agent receives the request and orchestrates the process:
   - Data Analyst agent retrieves similar projects
   - Knowledge Base agent provides relevant business rules
   - Quote Generator creates the initial quote
   - Pricing Optimizer fine-tunes pricing strategy
4. Response is returned to the UI for display
5. Quote is stored in the database if accepted

### Implementation Details

#### Vector Embeddings

The system uses OpenAI's embedding models to convert text into vector embeddings, enabling:

- Semantic search for similar projects
- Relevant business rule retrieval
- Pattern recognition in historical data

#### LLM Integration

Each agent leverages OpenAI's GPT models through structured prompts:

- Data analysis prompts focus on pattern recognition
- Quote generation prompts emphasize completeness and accuracy
- Pricing optimization prompts balance competitiveness and profitability

#### Mock Data Generation

For demonstration purposes, the system generates realistic mock data:

- Historical quotes with detailed breakdowns
- Customer profiles with relationship history
- Business rules reflecting industry practices
- Material pricing trends over time

## Future Enhancements

- Integration with ERP and CRM systems
- Fine-tuned domain-specific LLM models
- Automated learning from win/loss outcomes
- Competitor analysis capabilities

## License

This project is licensed under the MIT License - see the LICENSE file for details.