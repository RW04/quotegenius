```mermaid
graph TB
    subgraph Client
        UI[Web Interface]
    end
    
    subgraph Backend
        API[FastAPI Backend]
        
        subgraph "Agent System"
            Coordinator[Coordinator Agent]
            DataAnalyst[Data Analysis Agent]
            QuoteGenerator[Quote Generator Agent]
            PricingOptimizer[Pricing Optimizer Agent]
            KnowledgeAgent[Knowledge Base Agent]
        end
        
        subgraph "Data Layer"
            VectorDB[(Vector Database<br>Chroma/FAISS)]
            StructuredDB[(Structured Database<br>SQLite)]
        end
    end
    
    UI <--> API
    API <--> Coordinator
    
    Coordinator <--> DataAnalyst
    Coordinator <--> QuoteGenerator
    Coordinator <--> PricingOptimizer
    Coordinator <--> KnowledgeAgent
    
    DataAnalyst <--> VectorDB
    DataAnalyst <--> StructuredDB
    QuoteGenerator <--> VectorDB
    QuoteGenerator <--> StructuredDB
    PricingOptimizer <--> VectorDB
    PricingOptimizer <--> StructuredDB
    KnowledgeAgent <--> VectorDB
    
    subgraph "External Systems"
        ERP[Customer ERP]
        CRM[Customer CRM]
    end
    
    API <-.-> ERP
    API <-.-> CRM
    
    classDef primary fill:#264653,stroke:#2a9d8f,stroke-width:2px,color:#ffffff;
    classDef secondary fill:#e9c46a,stroke:#f4a261,stroke-width:1px,color:#264653;
    classDef storage fill:#e76f51,stroke:#e63946,stroke-width:1px,color:#ffffff;
    classDef external fill:#f1faee,stroke:#a8dadc,stroke-width:1px,color:#1d3557,stroke-dasharray: 5 5;
    
    class Coordinator,API primary;
    class DataAnalyst,QuoteGenerator,PricingOptimizer,KnowledgeAgent secondary;
    class VectorDB,StructuredDB storage;
    class ERP,CRM,UI external;
```
