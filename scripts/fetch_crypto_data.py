# scripts/fetch_crypto_data.py
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class TokenScanner:
    def __init__(self):
        self.dexscreener_api = "https://api.dexscreener.com/latest/dex/tokens/"
        self.coingecko_api = "https://api.coingecko.com/api/v3/"
        
    def scan_token(self, token_address: str) -> Dict:
        """Comprehensive token scanning similar to DexScreener/Birdeye"""
        token_data = {
            'basic_info': self._get_basic_info(token_address),
            'market_data': self._get_market_data(token_address),
            'holder_analysis': self._analyze_holders(token_address),
            'liquidity_analysis': self._analyze_liquidity(token_address),
            'trading_patterns': self._analyze_trading_patterns(token_address),
            'risk_indicators': self._calculate_risk_indicators(token_address)
        }
        return token_data
    
    def _get_basic_info(self, token_address: str) -> Dict:
        """Get basic token information"""
        try:
            response = requests.get(f"{self.dexscreener_api}{token_address}")
            data = response.json()
            
            return {
                'name': data.get('name'),
                'symbol': data.get('symbol'),
                'total_supply': data.get('totalSupply'),
                'creation_time': data.get('creationTime'),
                'verified': data.get('verified', False)
            }
        except Exception as e:
            print(f"Error fetching basic info: {e}")
            return {}

    def _get_market_data(self, token_address: str) -> Dict:
        """Get detailed market data"""
        return {
            'price_usd': 0.0,
            'price_change_24h': 0.0,
            'volume_24h': 0,
            'market_cap': 0,
            'fully_diluted_valuation': 0
        }

    def _analyze_holders(self, token_address: str) -> Dict:
        """Analyze token holders similar to Birdeye"""
        return {
            'total_holders': 0,
            'top_holders': [],
            'holder_distribution': {},
            'suspicious_holders': []
        }

    def _analyze_liquidity(self, token_address: str) -> Dict:
        """Analyze liquidity pools"""
        return {
            'total_liquidity': 0,
            'liquidity_pairs': [],
            'locked_liquidity': 0,
            'liquidity_removals_24h': []
        }

    def _analyze_trading_patterns(self, token_address: str) -> Dict:
        """Analyze trading patterns for suspicious activity"""
        return {
            'buy_sell_ratio': 0,
            'average_transaction_size': 0,
            'unusual_patterns': [],
            'whale_movements': []
        }

    def _calculate_risk_indicators(self, token_address: str) -> Dict:
        """Calculate risk indicators similar to token scanners"""
        return {
            'risk_level': 'LOW',
            'risk_factors': [],
            'honeypot_risk': False,
            'contract_risks': [],
            'ownership_risks': []
        }

class FraudDetectionIndicators:
    @staticmethod
    def check_honeypot_risk(token_data: Dict) -> bool:
        """Check if token might be a honeypot"""
        risk_factors = []
        
        # Check sell tax
        if token_data.get('sell_tax', 0) > 10:
            risk_factors.append('High sell tax')
            
        # Check buy tax
        if token_data.get('buy_tax', 0) > 10:
            risk_factors.append('High buy tax')
            
        # Check liquidity
        if token_data.get('liquidity', 0) < 10000:  # $10k minimum
            risk_factors.append('Low liquidity')
            
        return len(risk_factors) > 0, risk_factors

    @staticmethod
    def analyze_contract_risks(contract_data: Dict) -> List[str]:
        """Analyze smart contract for common risks"""
        risks = []
        
        if contract_data.get('is_proxy', False):
            risks.append('Proxy contract - upgradeable')
            
        if contract_data.get('has_mint_function', False):
            risks.append('Mint function present')
            
        if not contract_data.get('ownership_renounced', False):
            risks.append('Ownership not renounced')
            
        return risks

    @staticmethod
    def check_liquidity_risks(liquidity_data: Dict) -> List[str]:
        """Analyze liquidity-related risks"""
        risks = []
        
        if liquidity_data.get('locked_percentage', 0) < 80:
            risks.append('Low locked liquidity')
            
        if liquidity_data.get('largest_pool_percentage', 0) > 90:
            risks.append('Concentrated liquidity')
            
        return risks

if __name__ == "__main__":
    # Example usage
    scanner = TokenScanner()
    
    # Example token address (Replace with actual token address)
    token_address = "0x123..."
    
    # Scan token
    token_data = scanner.scan_token(token_address)
    
    # Print results
    print("\nToken Scan Results:")
    for category, data in token_data.items():
        print(f"\n{category.upper()}:")
        print(data)