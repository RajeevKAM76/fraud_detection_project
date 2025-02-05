import pandas as pd
import numpy as np
from datetime import datetime
from config.settings import MIN_WALLET_AGE_DAYS

class FeatureEngineer:
    def __init__(self):
        self.min_wallet_age = MIN_WALLET_AGE_DAYS
    
    def create_features(self, df):
        """Create features for fraud detection"""
        df = self._add_time_features(df)
        df = self._add_transaction_features(df)
        df = self._add_wallet_features(df)
        return df
    
    def _add_time_features(self, df):
        df["hour"] = pd.to_datetime(df["timestamp"]).dt.hour
        df["day_of_week"] = pd.to_datetime(df["timestamp"]).dt.dayofweek
        df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
        df["is_night"] = df["hour"].isin(range(0, 6)).astype(int)
        return df
    
    def _add_transaction_features(self, df):
        df["tx_count_24h"] = df.groupby("wallet_address")["timestamp"].transform(
            lambda x: x.rolling("24H").count()
        )
        df["amount_zscore"] = df.groupby("wallet_address")["amount"].transform(
            lambda x: (x - x.mean()) / x.std()
        )
        return df
    
    def _add_wallet_features(self, df):
        df["wallet_age_days"] = (
            datetime.now() - pd.to_datetime(df["wallet_creation_date"])
        ).dt.days
        df["is_new_wallet"] = (df["wallet_age_days"] < self.min_wallet_age).astype(int)
        return df