# generate_mock_data.py
import os
import json
import random
import csv
from datetime import datetime, timedelta
import pandas as pd
import sqlite3

# Ensure data directories exist
os.makedirs("./data/vector_db/quotes", exist_ok=True)
os.makedirs("./data/vector_db/projects", exist_ok=True)
os.makedirs("./data/vector_db/business_rules", exist_ok=True)
os.makedirs("./data/structured_db", exist_ok=True)
os.makedirs("./data/mock_files", exist_ok=True)

print("Generating mock manufacturing quote data...")

# Define constants for realistic data generation
CUSTOMERS = [
    {"id": "cust-101", "name": "Aerospace Dynamics", "industry": "Aerospace", "relationship_years": 5, "credit_score": 85},
    {"id": "cust-102", "name": "Industrial Solutions Inc.", "industry": "Manufacturing", "relationship_years": 3, "credit_score": 72},
    {"id": "cust-103", "name": "MedTech Innovations", "industry": "Medical", "relationship_years": 7, "credit_score": 90},
    {"id": "cust-104", "name": "Precision Manufacturing", "industry": "Automotive", "relationship_years": 4, "credit_score": 78},
    {"id": "cust-105", "name": "EnergyTech Systems", "industry": "Energy", "relationship_years": 2, "credit_score": 67},
    {"id": "cust-106", "name": "Global Construction", "industry": "Construction", "relationship_years": 1, "credit_score": 70}
]

MATERIALS = [
    {"name": "Aluminum Alloy 6061", "unit": "kg", "base_price": 15.50},
    {"name": "Stainless Steel 304", "unit": "kg", "base_price": 12.75},
    {"name": "Carbon Fiber Sheet", "unit": "sqm", "base_price": 85.00},
    {"name": "Titanium Grade 5", "unit": "kg", "base_price": 110.00},
    {"name": "High-Density Polyethylene", "unit": "kg", "base_price": 8.25},
    {"name": "Copper Rod", "unit": "kg", "base_price": 22.50},
    {"name": "Precision Bearings", "unit": "units", "base_price": 45.00},
    {"name": "Hydraulic Cylinders", "unit": "units", "base_price": 155.00},
    {"name": "Electronic Control Boards", "unit": "units", "base_price": 210.00},
    {"name": "Industrial Fasteners", "unit": "boxes", "base_price": 35.00}
]

PROJECT_TYPES = [
    {"type": "Custom Machining", "description_template": "Precision machining of {material} components for {industry} applications with tolerances of {tolerance}."},
    {"type": "Assembly System", "description_template": "Design and manufacturing of automated assembly systems for {product} production with a capacity of {capacity} units per hour."},
    {"type": "Prototyping", "description_template": "Rapid prototyping of {product} using {material} with {feature} capabilities."},
    {"type": "Maintenance Equipment", "description_template": "Manufacturing of specialized maintenance equipment for {industry} sector focusing on {feature}."},
    {"type": "Testing Apparatus", "description_template": "Design and fabrication of testing apparatus for {industry} with {feature} measurement capabilities."}
]

INDUSTRIES = ["aerospace", "automotive", "medical", "electronics", "energy", "defense", "consumer goods"]
PRODUCTS = ["valves", "pumps", "controllers", "sensors", "actuators", "frames", "housings", "assemblies"]
FEATURES = ["high-precision", "temperature-resistant", "corrosion-resistant", "lightweight", "high-strength", "miniaturized"]
TOLERANCES = ["±0.01mm", "±0.05mm", "±0.1mm", "±0.005 inches", "±0.001 inches"]
CAPACITIES = ["100-150", "250-300", "500-600", "1000+"]

# -----------------------------------------------------------
# Generate SQLite database with quotes and customer data
# -----------------------------------------------------------

print("Generating structured database...")

conn = sqlite3.connect("./data/structured_db/quotes.db")
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS quotes (
    quote_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    project_name TEXT NOT NULL,
    total_price REAL NOT NULL,
    timestamp TEXT NOT NULL,
    quote_data TEXT NOT NULL,
    status TEXT DEFAULT 'pending'
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    industry TEXT,
    relationship_length INTEGER,
    credit_score INTEGER
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_id TEXT NOT NULL,
    feedback_text TEXT,
    accepted BOOLEAN NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (quote_id) REFERENCES quotes (quote_id)
)
''')

# Insert customer data
for customer in CUSTOMERS:
    cursor.execute(
        "INSERT OR REPLACE INTO customers (customer_id, customer_name, industry, relationship_length, credit_score) VALUES (?, ?, ?, ?, ?)",
        (customer["id"], customer["name"], customer["industry"], customer["relationship_years"], customer["credit_score"])
    )

# Generate quotes
quotes = []
for i in range(1, 51):
    # Select a random customer
    customer = random.choice(CUSTOMERS)
    
    # Select a random project type
    project_type = random.choice(PROJECT_TYPES)
    
    # Generate a description using the template
    description = project_type["description_template"].format(
        material=random.choice(MATERIALS)["name"],
        industry=random.choice(INDUSTRIES),
        product=random.choice(PRODUCTS),
        feature=random.choice(FEATURES),
        tolerance=random.choice(TOLERANCES),
        capacity=random.choice(CAPACITIES)
    )
    
    # Generate random materials for the quote
    quote_materials = []
    num_materials = random.randint(3, 8)
    for j in range(num_materials):
        material = random.choice(MATERIALS)
        quantity = random.randint(5, 500)
        quote_materials.append({
            "name": material["name"],
            "quantity": quantity,
            "unit": material["unit"],
            "unit_price": material["base_price"] * random.uniform(0.9, 1.1),
            "total": quantity * material["base_price"] * random.uniform(0.9, 1.1)
        })
    
    # Calculate labor costs
    labor_hours = random.randint(80, 1000)
    labor_rate = random.uniform(75, 120)
    labor_cost = labor_hours * labor_rate
    
    # Calculate equipment costs
    equipment_cost = random.uniform(0.1, 0.3) * sum(m["total"] for m in quote_materials)
    
    # Calculate overhead
    overhead_rate = random.uniform(0.15, 0.25)
    overhead_cost = overhead_rate * (sum(m["total"] for m in quote_materials) + labor_cost)
    
    # Calculate profit margin
    margin_rate = random.uniform(0.18, 0.35)
    costs = sum(m["total"] for m in quote_materials) + labor_cost + equipment_cost + overhead_cost
    profit_margin = costs * margin_rate / (1 - margin_rate)
    
    # Calculate total price
    total_price = costs + profit_margin
    
    # Generate quote timestamp (random date in last 180 days)
    days_ago = random.randint(1, 180)
    quote_date = datetime.now() - timedelta(days=days_ago)
    
    # Determine status (weighted random)
    status_weights = {"accepted": 0.6, "rejected": 0.3, "pending": 0.1}
    status = random.choices(
        list(status_weights.keys()),
        weights=list(status_weights.values()),
        k=1
    )[0]
    
    # Create quote data
    quote_id = f"QG-{quote_date.strftime('%Y%m%d')}-{i:04d}"
    
    quote_data = {
        "quote_id": quote_id,
        "customer_id": customer["id"],
        "project_name": f"{project_type['type']} - {random.choice(PRODUCTS).capitalize()} {random.randint(100, 999)}",
        "project_description": description,
        "total_price": total_price,
        "timestamp": quote_date.isoformat(),
        "materials": quote_materials,
        "labor": {
            "hours": labor_hours,
            "rate": labor_rate,
            "total": labor_cost
        },
        "breakdown": {
            "materials": sum(m["total"] for m in quote_materials),
            "labor": labor_cost,
            "equipment": equipment_cost,
            "overhead": overhead_cost,
            "profit_margin": profit_margin
        },
        "confidence_score": random.randint(75, 98),
        "status": status
    }
    
    # Insert into database
    cursor.execute(
        "INSERT INTO quotes (quote_id, customer_id, project_name, total_price, timestamp, quote_data, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            quote_id,
            customer["id"],
            quote_data["project_name"],
            total_price,
            quote_date.isoformat(),
            json.dumps(quote_data),
            status
        )
    )
    
    # Add feedback for non-pending quotes
    if status != "pending":
        feedback_options = {
            "accepted": [
                "Your competitive pricing and detailed breakdown gave us confidence in your quote.",
                "The timeline works well with our project schedule. We appreciate the detailed approach.",
                "Your team's expertise in optimizing the manufacturing process was evident in the proposal.",
                "The quote addressed all our technical requirements and offered good value.",
                "We were impressed by the quality guarantees and service level agreement included."
            ],
            "rejected": [
                "We found a more competitive price from another supplier.",
                "The timeline was too long for our project needs.",
                "Your material specifications didn't fully meet our technical requirements.",
                "We decided to go with a supplier who has more experience in our specific industry.",
                "The payment terms weren't flexible enough for our current cash flow situation."
            ]
        }
        
        feedback_text = random.choice(feedback_options[status])
        
        cursor.execute(
            "INSERT INTO feedback (quote_id, feedback_text, accepted, timestamp) VALUES (?, ?, ?, ?)",
            (
                quote_id,
                feedback_text,
                status == "accepted",
                quote_date.isoformat()
            )
        )
    
    quotes.append(quote_data)
    
conn.commit()

print(f"Added {len(quotes)} quotes to the database")

# -----------------------------------------------------------
# Generate CSV files with historical quote data
# -----------------------------------------------------------

print("Generating CSV files...")

# Historical quotes summary
historical_quotes = []
for i in range(1, 201):  # Generate 200 historical quotes
    quote_date = datetime.now() - timedelta(days=random.randint(180, 730))  # 6 months to 2 years ago
    customer = random.choice(CUSTOMERS)
    
    # Determine outcome (weighted random)
    won = random.random() < 0.65
    
    # Calculate some realistic values
    material_cost = random.uniform(15000, 200000)
    labor_cost = random.uniform(10000, 150000)
    overhead = random.uniform(5000, 50000)
    margin = random.uniform(0.15, 0.35)
    total_cost = material_cost + labor_cost + overhead
    quoted_price = total_cost / (1 - margin)
    
    # Response time in days
    response_time = random.randint(1, 10)
    
    historical_quotes.append({
        "quote_id": f"HIST-{quote_date.strftime('%Y%m%d')}-{i:04d}",
        "date": quote_date.strftime("%Y-%m-%d"),
        "customer_name": customer["name"],
        "customer_id": customer["id"],
        "industry": customer["industry"],
        "project_type": random.choice(PROJECT_TYPES)["type"],
        "quoted_price": quoted_price,
        "material_cost": material_cost,
        "labor_cost": labor_cost,
        "overhead": overhead,
        "margin_percentage": margin * 100,
        "response_time_days": response_time,
        "won": won,
        "reason_if_lost": "" if won else random.choice([
            "Price too high", "Timeline issues", "Technical requirements", 
            "Competitor relationship", "Budget constraints"
        ])
    })

# Write to CSV
with open("./data/mock_files/historical_quotes.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=historical_quotes[0].keys())
    writer.writeheader()
    writer.writerows(historical_quotes)

# Generate material pricing history
materials_history = []
for material in MATERIALS:
    base_price = material["base_price"]
    
    # Generate monthly prices for the last 24 months
    for i in range(24, 0, -1):
        month_date = datetime.now().replace(day=1) - timedelta(days=30*i)
        
        # Add some trend and volatility
        trend_factor = 1 + (0.005 * (24-i))  # Slight upward trend
        volatility = random.uniform(-0.05, 0.08)
        
        price = base_price * trend_factor * (1 + volatility)
        
        materials_history.append({
            "material": material["name"],
            "date": month_date.strftime("%Y-%m-%d"),
            "price_per_unit": price,
            "unit": material["unit"]
        })

# Write to CSV
with open("./data/mock_files/material_pricing_history.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=materials_history[0].keys())
    writer.writeheader()
    writer.writerows(materials_history)

# -----------------------------------------------------------
# Generate sample project specification PDFs (mock content)
# -----------------------------------------------------------

print("Generating mock specification documents...")

# Just create text files with mock content instead of actual PDFs
for i in range(1, 6):
    project_type = random.choice(PROJECT_TYPES)
    material = random.choice(MATERIALS)["name"]
    industry = random.choice(INDUSTRIES)
    product = random.choice(PRODUCTS)
    
    spec_content = f"""
TECHNICAL SPECIFICATION DOCUMENT
===============================

Project: {project_type['type']} - {product.capitalize()} {random.randint(100, 999)}
Client: {random.choice(CUSTOMERS)['name']}
Date: {(datetime.now() - timedelta(days=random.randint(10, 90))).strftime('%Y-%m-%d')}

1. SCOPE
--------
{project_type['description_template'].format(
    material=material,
    industry=industry,
    product=product,
    feature=random.choice(FEATURES),
    tolerance=random.choice(TOLERANCES),
    capacity=random.choice(CAPACITIES)
)}

2. MATERIAL REQUIREMENTS
-----------------------
Primary Material: {material}
Quantity Required: {random.randint(50, 500)} {random.choice(['kg', 'units', 'sqm'])}
Specifications: 
- {random.choice(['Heat treated', 'Anodized', 'Cold rolled', 'Tempered', 'Galvanized'])}
- {random.choice(['Grade A', 'Commercial grade', 'Military spec', 'Aerospace grade', 'Medical grade'])}
- Surface finish: {random.choice(['Polished', 'Brushed', 'Satin', 'Matte', 'High gloss'])}

3. MANUFACTURING REQUIREMENTS
----------------------------
Tolerances: {random.choice(TOLERANCES)}
Production Volume: {random.randint(100, 10000)} units
Quality Control: {random.choice(['ISO 9001', 'AS9100', 'ISO 13485', 'IATF 16949'])} standards apply

4. TIMELINE
----------
Lead Time Required: {random.randint(2, 12)} weeks
Delivery Schedule: {random.choice(['Single delivery', 'Phased delivery', 'Just-in-time delivery'])}

5. SPECIAL INSTRUCTIONS
---------------------
{random.choice([
    "Parts must be individually wrapped and labeled",
    "Temperature-controlled shipping required",
    "Certificate of conformance required for each batch",
    "First article inspection required before full production",
    "Material traceability documentation required"
])}

APPROVED BY:
{random.choice(['J. Smith', 'R. Johnson', 'A. Williams', 'L. Brown', 'M. Jones'])}
Engineering Manager
"""

    with open(f"./data/mock_files/project_spec_{i}.txt", "w") as f:
        f.write(spec_content)

# -----------------------------------------------------------
# Generate business rules data (for vector DB)
# -----------------------------------------------------------

print("Generating business rules data...")

# Standard rules
standard_rules = [
    "Standard markup for raw materials is 15-20% depending on market volatility.",
    "Labor rates must include 25% overhead for benefits and facility costs.",
    "Quotes over $100,000 require senior management approval before submission.",
    "Projects with timelines exceeding 3 months require milestone payment terms.",
    "Add contingency of 10% for projects with high technical complexity.",
    "Rush orders (delivery less than standard lead time) include 15% premium.",
    "First-time customer discounts capped at 5% of total quote value.",
    "Volume discounts apply on material costs: 5% for orders >$50K, 8% for orders >$100K.",
    "Quotes are valid for 30 days unless otherwise specified.",
    "Minimum order value is $5,000 for new customers, $2,500 for existing customers."
]

# Customer-specific rules
customer_rules = [
    {"customer_id": "cust-101", "rule": "Aerospace Dynamics has negotiated a 5% volume discount on orders over $100,000."},
    {"customer_id": "cust-101", "rule": "Aerospace Dynamics requires dedicated quality assurance staff on projects over $200,000."},
    {"customer_id": "cust-102", "rule": "Industrial Solutions Inc. has 45-day payment terms instead of standard 30-day."},
    {"customer_id": "cust-103", "rule": "MedTech Innovations requires ISO 13485 certification documentation with all quotes."},
    {"customer_id": "cust-103", "rule": "MedTech Innovations receives priority scheduling, adjust lead times down by 15%."},
    {"customer_id": "cust-104", "rule": "Precision Manufacturing has negotiated fixed pricing on stainless steel components through Q2 2025."},
    {"customer_id": "cust-105", "rule": "EnergyTech Systems requires detailed sustainability documentation for all materials."}
]

# Write to JSON file for later loading into vector DB
with open("./data/mock_files/business_rules.json", "w") as f:
    json.dump({
        "standard_rules": [{"rule_id": f"std-{i+1}", "rule_type": "general", "rule_description": rule} 
                          for i, rule in enumerate(standard_rules)],
        "customer_rules": [{"rule_id": f"cust-rule-{i+1}", "rule_type": "customer-specific", 
                          "customer_id": rule["customer_id"], "rule_description": rule["rule"]} 
                          for i, rule in enumerate(customer_rules)]
    }, f, indent=2)

print("Mock data generation complete!")