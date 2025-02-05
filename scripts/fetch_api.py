import requests
import pandas as pd
from datetime import datetime
import sys
import os
from sqlalchemy import create_engine
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from config.settings import (
    DEXSCREENER_BASE_URL,
    SUPPORTED_CHAINS,
    DATABASE_URL,
    DATA_DIR,
    LOG_LEVEL
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DexScreenerAPI:
    def __init__(self):
        self.base_url = DEXSCREENER_BASE_URL
        self.db_engine = create_engine(DATABASE_URL)
        
    def fetch_token_data(self, chain_id, token_addresses):
        """
        Fetch token data from DexScreener API
        """
        if chain_id not in SUPPORTED_CHAINS:
            raise ValueError(f"Unsupported chain_id. Must be one of {list(SUPPORTED_CHAINS.keys())}")
            
        url = f"{self.base_url}/{chain_id}/{token_addresses}"
        logger.info(f"Fetching data from: {url}")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            logger.info("Successfully fetched data from API")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data: {e}")
            return None
            
    def process_token_data(self, data):
        """
        Process raw token data into a pandas DataFrame
        """
        if not data:
            logger.warning("No data to process")
            return pd.DataFrame()
            
        processed_data = []
        for pair in data:
            processed_pair = {
                'chain_id': pair.get('chainId'),
                'dex_id': pair.get('dexId'),
                'pair_address': pair.get('pairAddress'),
                'base_token_address': pair.get('baseToken', {}).get('address'),
                'base_token_name': pair.get('baseToken', {}).get('name'),
                'quote_token_address': pair.get('quoteToken', {}).get('address'),
                'price_usd': pair.get('priceUsd'),
                'liquidity_usd': pair.get('liquidity', {}).get('usd'),
                'volume_24h': pair.get('volume', {}).get('h24'),
                'price_change_24h': pair.get('priceChange', {}).get('h24'),
                'timestamp': datetime.now().isoformat()
            }
            processed_data.append(processed_pair)
        
        df = pd.DataFrame(processed_data)
        logger.info(f"Processed {len(df)} records")
        return df
        
    def save_to_csv(self, df, filename):
        """
        Save processed data to CSV
        """
        if df.empty:
            logger.warning("No data to save to CSV")
            return
            
        output_path = os.path.join(DATA_DIR, filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info(f"Data saved to {output_path}")

    def save_to_database(self, df, table_name='token_data'):
        """
        Save processed data to PostgreSQL database
        """
        if df.empty:
            logger.warning("No data to save to database")
            return
            
        try:
            df.to_sql(
                table_name,
                self.db_engine,
                if_exists='append',
                index=False
            )
            logger.info(f"Successfully saved {len(df)} records to database table {table_name}")
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
            raise

def main():
    try:
        api = DexScreenerAPI()
        
        # Example usage - you should replace these with actual addresses
        token_addresses = os.getenv('TOKEN_ADDRESSES', "0x123,0x456")
        chain_id = os.getenv('CHAIN_ID', "ethereum")
        
        logger.info(f"Starting data fetch for chain: {chain_id}")
        data = api.fetch_token_data(chain_id, token_addresses)
        
        if data:
            df = api.process_token_data(data)
            
            # Save to both CSV and database
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            api.save_to_csv(df, f"dex_data_{timestamp}.csv")
            api.save_to_database(df)
            
            logger.info("Data processing and storage completed successfully")
        else:
            logger.warning("No data was fetched from the API")
            
    except Exception as e:
        logger.error(f"An error occurred in main execution: {e}")
        raise

if __name__ == "__main__":
    main()