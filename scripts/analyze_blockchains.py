import pandas as pd
from config.settings import SUSPICIOUS_CHAINS

class BlockchainAnalyzer:
    def __init__(self):
        self.high_risk_chains = SUSPICIOUS_CHAINS
    
    def analyze_chain_risk(self, df):
        """Analyze blockchain risk patterns"""
        df["chain_risk_score"] = df["blockchain"].apply(
            lambda x: 1 if x in self.high_risk_chains else 0
        )
        
        risk_analysis = {
            "high_risk_transactions": df[df["chain_risk_score"] == 1].shape[0],
            "risk_by_chain": df.groupby("blockchain")["chain_risk_score"].mean(),
            "volume_by_chain": df.groupby("blockchain")["amount"].sum()
        }
        
        return df, risk_analysis