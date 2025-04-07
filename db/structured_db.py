# db/structured_db.py
import sqlite3
import json
import os
import logging
from typing import Dict, Any, List, Optional

class StructuredDB:
    """
    Structured database for storing and retrieving quote data,
    customer information, and feedback in a relational format.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db_path = "./data/structured_db/quotes.db"
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Initialize database
        self._initialize_db()
        
    def _initialize_db(self):
        """Initialize database tables if they don't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create quotes table
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
            
            # Create customers table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                industry TEXT,
                relationship_length INTEGER,
                credit_score INTEGER
            )
            ''')
            
            # Create feedback table
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
            
            conn.commit()
            conn.close()
            
            # Seed database if it's empty
            if os.environ.get("SEED_DB", "false").lower() == "true":
                self._seed_database()
                
        except Exception as e:
            self.logger.error(f"Database initialization error: {str(e)}")
            
    def store_quote(self, quote_data: Dict[str, Any]) -> bool:
        """Store a new quote in the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                '''
                INSERT INTO quotes 
                (quote_id, customer_id, project_name, total_price, timestamp, quote_data) 
                VALUES (?, ?, ?, ?, ?, ?)
                ''',
                (
                    quote_data["quote_id"],
                    quote_data["customer_id"],
                    quote_data["project_name"],
                    quote_data["total_price"],
                    quote_data["timestamp"],
                    json.dumps(quote_data)
                )
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Error storing quote: {str(e)}")
            return False
            
    def get_quote(self, quote_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a quote by ID."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT quote_data FROM quotes WHERE quote_id = ?",
                (quote_id,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return json.loads(result[0])
            return None
        except Exception as e:
            self.logger.error(f"Error retrieving quote: {str(e)}")
            return None
            
    def record_feedback(self, quote_id: str, feedback: str, accepted: bool) -> bool:
        """Record customer feedback on a quote."""
        try:
            from datetime import datetime
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert feedback
            cursor.execute(
                '''
                INSERT INTO feedback
                (quote_id, feedback_text, accepted, timestamp)
                VALUES (?, ?, ?, ?)
                ''',
                (
                    quote_id,
                    feedback,
                    accepted,
                    datetime.now().isoformat()
                )
            )
            
            # Update quote status
            new_status = "accepted" if accepted else "rejected"
            cursor.execute(
                '''
                UPDATE quotes
                SET status = ?
                WHERE quote_id = ?
                ''',
                (new_status, quote_id)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Error recording feedback: {str(e)}")
            return False
    
    def get_customer_data(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve customer data by ID."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM customers WHERE customer_id = ?",
                (customer_id,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    "customer_id": result[0],
                    "customer_name": result[1],
                    "industry": result[2],
                    "relationship_length": result[3],
                    "credit_score": result[4]
                }
            return None
        except Exception as e:
            self.logger.error(f"Error retrieving customer data: {str(e)}")
            return None
    
    def get_customer_quotes(self, customer_id: str) -> List[Dict[str, Any]]:
        """Retrieve all quotes for a specific customer."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT quote_data 
                FROM quotes 
                WHERE customer_id = ? 
                ORDER BY timestamp DESC
                """,
                (customer_id,)
            )
            
            results = cursor.fetchall()
            conn.close()
            
            return [json.loads(row[0]) for row in results]
        except Exception as e:
            self.logger.error(f"Error retrieving customer quotes: {str(e)}")
            return []
    
    def get_quote_analytics(self) -> Dict[str, Any]:
        """Get analytics data on quotes - win rates, average margins, etc."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total quotes count
            cursor.execute("SELECT COUNT(*) FROM quotes")
            total_quotes = cursor.fetchone()[0]
            
            # Get status distribution
            cursor.execute("""
                SELECT status, COUNT(*) 
                FROM quotes 
                GROUP BY status
            """)
            status_counts = {status: count for status, count in cursor.fetchall()}
            
            # Calculate average prices by status
            cursor.execute("""
                SELECT status, AVG(total_price) 
                FROM quotes 
                GROUP BY status
            """)
            avg_prices = {status: price for status, price in cursor.fetchall()}
            
            # Get monthly trends
            cursor.execute("""
                SELECT 
                    strftime('%Y-%m', timestamp) as month,
                    COUNT(*) as quote_count,
                    AVG(total_price) as avg_price,
                    SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) as accepted_count
                FROM quotes
                GROUP BY month
                ORDER BY month DESC
                LIMIT 12
            """)
            monthly_data = [{
                "month": row[0],
                "quote_count": row[1],
                "avg_price": row[2],
                "accepted_count": row[3],
                "win_rate": row[3] / row[1] if row[1] > 0 else 0
            } for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                "total_quotes": total_quotes,
                "status_distribution": status_counts,
                "avg_prices_by_status": avg_prices,
                "monthly_trends": monthly_data,
                "win_rate": status_counts.get("accepted", 0) / total_quotes if total_quotes > 0 else 0
            }
        except Exception as e:
            self.logger.error(f"Error retrieving quote analytics: {str(e)}")
            return {
                "error": str(e),
                "total_quotes": 0,
                "status_distribution": {},
                "monthly_trends": []
            }
    
    def _seed_database(self):
        """Seed the database with sample data for demonstration."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if we already have data
            cursor.execute("SELECT COUNT(*) FROM quotes")
            if cursor.fetchone()[0] > 0:
                conn.close()
                return
            
            # Add sample customers
            sample_customers = [
                ("cust-101", "Aerospace Dynamics", "Aerospace", 5, 85),
                ("cust-102", "Industrial Solutions Inc.", "Manufacturing", 2, 72),
                ("cust-103", "MedTech Innovations", "Medical", 3, 90)
            ]
            
            cursor.executemany(
                """
                INSERT INTO customers
                (customer_id, customer_name, industry, relationship_length, credit_score)
                VALUES (?, ?, ?, ?, ?)
                """,
                sample_customers
            )
            
            # Add sample quotes
            from datetime import datetime, timedelta
            import random
            
            for i in range(1, 20):
                quote_id = f"quote-{i:03d}"
                customer_id = f"cust-{random.choice([101, 102, 103])}"
                project_types = ["Assembly", "Fabrication", "Design", "Testing", "Maintenance"]
                project_name = f"{random.choice(['Industrial', 'Precision', 'Advanced'])} {random.choice(project_types)}"
                
                total_price = random.uniform(50000, 300000)
                timestamp = (datetime.now() - timedelta(days=random.randint(0, 180))).isoformat()
                
                # Generate random quote data
                quote_data = {
                    "quote_id": quote_id,
                    "customer_id": customer_id,
                    "project_name": project_name,
                    "total_price": total_price,
                    "timestamp": timestamp,
                    "breakdown": {
                        "materials": total_price * 0.6,
                        "labor": total_price * 0.3,
                        "overhead": total_price * 0.1
                    },
                    "confidence_score": random.randint(75, 98)
                }
                
                status = random.choice(["pending", "accepted", "rejected"])
                
                cursor.execute(
                    """
                    INSERT INTO quotes
                    (quote_id, customer_id, project_name, total_price, timestamp, quote_data, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        quote_id,
                        customer_id,
                        project_name,
                        total_price,
                        timestamp,
                        json.dumps(quote_data),
                        status
                    )
                )
                
                # Add feedback for some quotes
                if status in ["accepted", "rejected"]:
                    feedback_options = {
                        "accepted": [
                            "Price was competitive and timeline works for us.",
                            "Very detailed quote, gives us confidence in your abilities.",
                            "The breakdown helped us understand the value proposition."
                        ],
                        "rejected": [
                            "Found a more competitive price elsewhere.",
                            "Timeline was too long for our needs.",
                            "Materials specification didn't meet our requirements."
                        ]
                    }
                    
                    cursor.execute(
                        """
                        INSERT INTO feedback
                        (quote_id, feedback_text, accepted, timestamp)
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            quote_id,
                            random.choice(feedback_options[status]),
                            status == "accepted",
                            timestamp
                        )
                    )
            
            conn.commit()
            conn.close()
            self.logger.info("Database seeded with sample data")
            
        except Exception as e:
            self.logger.error(f"Error seeding database: {str(e)}")