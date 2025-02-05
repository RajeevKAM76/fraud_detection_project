import pandas as pd
import sqlite3
from datetime import datetime

class ResultsStorage:
    def __init__(self, db_path="data/fraud_results.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""
            CREATE TABLE IF NOT EXISTS fraud_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_address TEXT,
                fraud_probability REAL,
                timestamp DATETIME,
                blockchain TEXT,
                risk_factors TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def store_predictions(self, results_df):
        """Store fraud detection results"""
        conn = sqlite3.connect(self.db_path)
        
        results_df["timestamp"] = datetime.now()
        results_df.to_sql("fraud_predictions", conn, if_exists="append", index=False)
        
        conn.close()