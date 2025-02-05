# scripts/load_data.py
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from config.settings import DATA_PATH
import os

class DataLoader:
    def __init__(self):
        self.required_columns = [
            'timestamp', 'wallet_address', 'transaction_amount',
            'blockchain', 'source_country', 'transaction_type'
        ]
        self.data_path = DATA_PATH

    def load_data(self, source):
        """Load data from various sources with error handling"""
        try:
            if isinstance(source, str):
                if source.endswith('.csv'):
                    df = pd.read_csv(source)
                elif source.endswith('.json'):
                    df = pd.read_json(source)
                elif source.endswith('.xlsx'):
                    df = pd.read_excel(source)
                else:
                    # Attempt to load from API
                    response = requests.get(source)
                    df = pd.DataFrame(response.json())
            elif isinstance(source, pd.DataFrame):
                df = source.copy()
            else:
                raise ValueError("Unsupported data source")
            
            return self._process_data(df)
        except Exception as e:
            print(f"Error loading data: {e}")
            return None

    def _process_data(self, df):
        """Process and validate the dataframe"""
        # Check required columns
        missing_cols = set(self.required_columns) - set(df.columns)
        if missing_cols:
            print(f"Warning: Missing columns: {missing_cols}")
            # Add missing columns with NaN values
            for col in missing_cols:
                df[col] = np.nan

        # Convert timestamp to datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Clean and standardize data
        df = self._clean_data(df)
        
        return df

    def _clean_data(self, df):
        """Clean and standardize the dataframe"""
        # Remove duplicates
        df = df.drop_duplicates()

        # Handle missing values
        df['transaction_amount'] = df['transaction_amount'].fillna(0)
        df['blockchain'] = df['blockchain'].fillna('unknown')
        df['source_country'] = df['source_country'].fillna('unknown')
        df['transaction_type'] = df['transaction_type'].fillna('unknown')

        # Standardize text columns
        text_columns = ['blockchain', 'source_country', 'transaction_type']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].str.lower().str.strip()

        # Remove transactions with invalid amounts
        df = df[df['transaction_amount'] >= 0]

        return df

    def save_processed_data(self, df, filename):
        """Save processed data to CSV"""
        output_path = os.path.join(self.data_path, filename)
        df.to_csv(output_path, index=False)
        print(f"Data saved to {output_path}")

    def combine_multiple_sources(self, sources):
        """Combine data from multiple sources"""
        dfs = []
        for source in sources:
            df = self.load_data(source)
            if df is not None:
                dfs.append(df)
        
        if not dfs:
            return None
            
        combined_df = pd.concat(dfs, ignore_index=True)
        return self._process_data(combined_df)

    def load_batch_data(self, batch_size=1000):
        """Load data in batches to handle large datasets"""
        for filename in os.listdir(self.data_path):
            if filename.endswith('.csv'):
                file_path = os.path.join(self.data_path, filename)
                for chunk in pd.read_csv(file_path, chunksize=batch_size):
                    processed_chunk = self._process_data(chunk)
                    yield processed_chunk

if __name__ == "__main__":
    # Example usage
    loader = DataLoader()
    
    # Load from single source
    df = loader.load_data("data/transactions.csv")
    if df is not None:
        print("Single source data shape:", df.shape)
    
    # Load from multiple sources
    sources = [
        "data/transactions_1.csv",
        "data/transactions_2.csv",
        "https://api.example.com/data"
    ]
    combined_df = loader.combine_multiple_sources(sources)
    if combined_df is not None:
        print("Combined data shape:", combined_df.shape)
    
    # Load data in batches
    for batch in loader.load_batch_data(batch_size=1000):
        print("Processing batch of shape:", batch.shape)