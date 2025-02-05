import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL')
DATABASE_NAME = os.getenv('DATABASE_NAME')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')

# API Configuration
DEXSCREENER_BASE_URL = os.getenv('DEXSCREENER_BASE_URL', 'https://api.dexscreener.com/tokens/v1')
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
BSCSCAN_API_KEY = os.getenv('BSCSCAN_API_KEY')

# Supported Blockchain Networks
SUPPORTED_CHAINS = {
    "ethereum": "eth",
    "binance": "bsc",
    "polygon": "matic",
    "solana": "sol",
    "avalanche": "avax",
    "fantom": "ftm",
    "arbitrum": "arb"
}

# Analysis Configuration
SUSPICIOUS_TRANSACTION_THRESHOLD = float(os.getenv('SUSPICIOUS_TRANSACTION_THRESHOLD', 10000))  # in USD
PRICE_CHANGE_THRESHOLD = float(os.getenv('PRICE_CHANGE_THRESHOLD', 30))  # percentage
MINIMUM_LIQUIDITY = float(os.getenv('MINIMUM_LIQUIDITY', 5000))  # in USD
MAX_ADDRESSES_PER_REQUEST = int(os.getenv('MAX_ADDRESSES_PER_REQUEST', 30))

# Application Settings
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Data Paths
DATA_DIR = os.getenv('DATA_DIR', './data')
RESULTS_DIR = os.getenv('RESULTS_DIR', './data/results')
LOG_DIR = os.getenv('LOG_DIR', './logs')

# Create necessary directories
for directory in [DATA_DIR, RESULTS_DIR, LOG_DIR]:
    os.makedirs(directory, exist_ok=True)

# Database Table Names
TOKEN_DATA_TABLE = 'token_data'
FRAUD_ALERTS_TABLE = 'fraud_alerts'
BROWSER_ANALYSIS_TABLE = 'browser_analysis'
BLOCKCHAIN_ANALYSIS_TABLE = 'blockchain_analysis'

# API Request Settings
REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))  # seconds
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))

# Fraud Detection Settings
RISK_LEVELS = {
    'LOW': 1,
    'MEDIUM': 2,
    'HIGH': 3,
    'CRITICAL': 4
}

# Browser Analysis Settings
SUSPICIOUS_BROWSER_PATTERNS = [
    'old_version',
    'suspicious_user_agent',
    'known_bot_pattern',
    'proxy_indicator'
]

# Blockchain Analysis Settings
TRANSACTION_ANALYSIS_WINDOW = int(os.getenv('TRANSACTION_ANALYSIS_WINDOW', 24))  # hours

# Default Token Addresses for Testing
DEFAULT_TOKEN_ADDRESSES = os.getenv('DEFAULT_TOKEN_ADDRESSES', '0x123,0x456')

# Error Messages
ERROR_MESSAGES = {
    'API_ERROR': 'Error fetching data from API: {}',
    'DB_ERROR': 'Database error occurred: {}',
    'VALIDATION_ERROR': 'Validation error: {}',
    'CONFIG_ERROR': 'Configuration error: {}'
}
