import os
import sys
from pathlib import Path
from flask import Flask
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv()

# Import settings
from config.settings import DEBUG, DATABASE_URL

app = Flask(__name__)

# Configure app
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['DEBUG'] = DEBUG

if __name__ == '__main__':
    app.run(debug=DEBUG)