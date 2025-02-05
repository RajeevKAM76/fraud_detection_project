import pandas as pd
from config.settings import SUSPICIOUS_BROWSERS

class BrowserAnalyzer:
    def __init__(self):
        self.suspicious_browsers = SUSPICIOUS_BROWSERS
    
    def analyze_browser_patterns(self, df):
        """Analyze browser usage patterns for suspicious activity"""
        df["browser_risk_score"] = df["browser"].apply(
            lambda x: 1 if x in self.suspicious_browsers else 0
        )
        
        browser_analysis = {
            "suspicious_sessions": df[df["browser_risk_score"] == 1].shape[0],
            "risk_by_browser": df.groupby("browser")["browser_risk_score"].mean(),
            "usage_by_browser": df.groupby("browser").size()
        }
        
        return df, browser_analysis
