import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import lightgbm as lgb
from sklearn.metrics import classification_report, confusion_matrix
import joblib
from config.settings import FRAUD_THRESHOLD

class FraudDetector:
    def __init__(self):
        """Initialize the fraud detector with multiple models"""
        self.models = {
            'rf': RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            ),
            'xgb': xgb.XGBClassifier(
                max_depth=7,
                learning_rate=0.01,
                n_estimators=100,
                use_label_encoder=False,
                eval_metric='logloss'
            ),
            'lgb': lgb.LGBMClassifier(
                num_leaves=31,
                learning_rate=0.01,
                n_estimators=100
            )
        }
        self.scaler = StandardScaler()
        self.feature_columns = [
            'tx_count_24h',
            'amount_zscore',
            'is_weekend',
            'is_night',
            'is_new_wallet',
            'chain_risk_score',
            'browser_risk_score',
            'transaction_amount',
            'wallet_age_days'
        ]

    def prepare_features(self, df):
        """Prepare features for model training/prediction"""
        # Ensure all required features are present
        missing_cols = set(self.feature_columns) - set(df.columns)
        if missing_cols:
            for col in missing_cols:
                df[col] = 0
                print(f"Warning: Missing column {col} filled with zeros")
        
        X = df[self.feature_columns]
        
        # Handle missing values
        X = X.fillna(0)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        return pd.DataFrame(X_scaled, columns=self.feature_columns)

    def train(self, df, target_column='is_fraud'):
        """Train multiple models for ensemble prediction"""
        print("Starting model training...")
        
        # Prepare features
        X = self.prepare_features(df)
        y = df[target_column]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train and evaluate each model
        for name, model in self.models.items():
            print(f"\nTraining {name} model...")
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            
            print(f"\n{name.upper()} Model Performance:")
            print(classification_report(y_test, y_pred))
            print("\nConfusion Matrix:")
            print(confusion_matrix(y_test, y_pred))
            
            # Save trained model
            joblib.dump(model, f'models/{name}_model.pkl')
            
        # Save scaler
        joblib.dump(self.scaler, 'models/scaler.pkl')
        print("\nAll models trained and saved successfully!")

    def predict(self, df):
        """Make ensemble predictions"""
        try:
            # Prepare features
            X = self.prepare_features(df)
            
            # Get predictions from each model
            predictions = []
            for name, model in self.models.items():
                pred_proba = model.predict_proba(X)[:, 1]
                predictions.append(pred_proba)
            
            # Ensemble predictions (weighted average)
            weights = {'rf': 0.3, 'xgb': 0.4, 'lgb': 0.3}
            weighted_preds = []
            
            for name, pred in zip(self.models.keys(), predictions):
                weighted_preds.append(pred * weights[name])
            
            final_predictions = np.sum(weighted_preds, axis=0)
            
            # Add predictions to dataframe
            df['fraud_probability'] = final_predictions
            df['is_fraudulent'] = (final_predictions > FRAUD_THRESHOLD).astype(int)
            
            # Add risk factors
            df['risk_factors'] = self._get_risk_factors(df)
            
            return df
            
        except Exception as e:
            print(f"Error in prediction: {e}")
            return None

    def _get_risk_factors(self, df):
        """Identify specific risk factors for each transaction"""
        risk_factors = []
        
        for _, row in df.iterrows():
            factors = []
            
            if row['tx_count_24h'] > 100:
                factors.append('high_transaction_frequency')
            if row['amount_zscore'] > 3:
                factors.append('unusual_amount')
            if row['is_night'] == 1:
                factors.append('night_activity')
            if row['is_new_wallet'] == 1:
                factors.append('new_wallet')
            if row['chain_risk_score'] == 1:
                factors.append('high_risk_chain')
            if row['browser_risk_score'] == 1:
                factors.append('suspicious_browser')
            
            risk_factors.append(';'.join(factors) if factors else 'none')
        
        return risk_factors

    def load_models(self, models_dir='models/'):
        """Load pre-trained models"""
        try:
            for name in self.models.keys():
                model_path = f'{models_dir}{name}_model.pkl'
                self.models[name] = joblib.load(model_path)
            self.scaler = joblib.load(f'{models_dir}scaler.pkl')
            print("Models loaded successfully!")
        except Exception as e:
            print(f"Error loading models: {e}")

    def evaluate_predictions(self, df, actual_fraud_column='is_fraud'):
        """Evaluate model performance on new data"""
        if actual_fraud_column not in df.columns:
            print("No actual fraud labels available for evaluation")
            return None
            
        predictions = self.predict(df)
        if predictions is None:
            return None
            
        print("\nModel Performance Metrics:")
        print(classification_report(
            df[actual_fraud_column],
            predictions['is_fraudulent']
        ))
        
        return predictions


class TokenFraudDetector:
    def __init__(self):
        self.risk_thresholds = {
            'honeypot_risk': 0.7,
            'rugpull_risk': 0.8,
            'scam_risk': 0.75
        }

    def analyze_token_risks(self, token_data):
        """Analyze token for various fraud risks"""
        risk_scores = {
            'honeypot_risk': self._calculate_honeypot_risk(token_data),
            'rugpull_risk': self._calculate_rugpull_risk(token_data),
            'scam_risk': self._calculate_scam_risk(token_data),
            'overall_risk': 0.0
        }
        
        # Calculate overall risk
        risk_scores['overall_risk'] = sum(
            score for key, score in risk_scores.items() 
            if key != 'overall_risk'
        ) / 3
        
        return risk_scores
    
    def _calculate_honeypot_risk(self, token_data):
        """Calculate risk of token being a honeypot"""
        risk_score = 0
        risk_factors = []
        
        # Check sell tax
        if token_data.get('sell_tax', 0) > 10:
            risk_score += 0.3
            risk_factors.append('High sell tax')
        
        # Check buy tax
        if token_data.get('buy_tax', 0) > 10:
            risk_score += 0.2
            risk_factors.append('High buy tax')
        
        # Check successful sells
        if token_data.get('successful_sells', 0) < 10:
            risk_score += 0.5
            risk_factors.append('Few successful sells')
        
        return min(risk_score, 1.0)
    
    def _calculate_rugpull_risk(self, token_data):
        """Calculate risk of token being a potential rug pull"""
        risk_score = 0
        
        # Check liquidity lock
        locked_liquidity = token_data.get('locked_liquidity', 0)
        if locked_liquidity < 50:  # Less than 50% locked
            risk_score += 0.4
        
        # Check owner wallet concentration
        owner_percentage = token_data.get('owner_percentage', 0)
        if owner_percentage > 50:  # Owner holds more than 50%
            risk_score += 0.3
        
        # Check contract ownership
        if not token_data.get('ownership_renounced', False):
            risk_score += 0.3
        
        return min(risk_score, 1.0)
    
    def _calculate_scam_risk(self, token_data):
        """Calculate general scam risk based on various factors"""
        risk_score = 0
        
        # Check verified status
        if not token_data.get('verified', False):
            risk_score += 0.2
        
        # Check age of token
        token_age = token_data.get('age_days', 0)
        if token_age < 7:  # Less than a week old
            risk_score += 0.3
        
        # Check trading volume
        volume_24h = token_data.get('volume_24h', 0)
        if volume_24h < 10000:  # Less than $10k daily volume
            risk_score += 0.2
        
        # Check holder distribution
        holder_count = token_data.get('holder_count', 0)
        if holder_count < 100:  # Less than 100 holders
            risk_score += 0.3
        
        return min(risk_score, 1.0)

    def get_risk_report(self, token_address):
        """Generate comprehensive risk report"""
        scanner = TokenScanner()  # Note: You'll need to implement TokenScanner class
        token_data = scanner.scan_token(token_address)
        risk_scores = self.analyze_token_risks(token_data)
        
        return {
            'token_address': token_address,
            'risk_scores': risk_scores,
            'token_data': token_data,
            'recommendations': self._generate_recommendations(risk_scores)
        }

    def _generate_recommendations(self, risk_scores):
        """Generate recommendations based on risk scores"""
        recommendations = []
        
        if risk_scores['honeypot_risk'] > self.risk_thresholds['honeypot_risk']:
            recommendations.append("HIGH RISK: Potential honeypot. Verify sell capability.")
        
        if risk_scores['rugpull_risk'] > self.risk_thresholds['rugpull_risk']:
            recommendations.append("HIGH RISK: Potential rug pull. Check liquidity locks.")
        
        if risk_scores['scam_risk'] > self.risk_thresholds['scam_risk']:
            recommendations.append("HIGH RISK: Multiple scam indicators present.")
        
        return recommendations


if __name__ == "__main__":
    # Example usage for FraudDetector
    import pandas as pd
    
    # Create sample data
    sample_data = pd.DataFrame({
        'tx_count_24h': [5, 150, 20, 300],
        'amount_zscore': [0.5, 4.0, 1.0, 5.0],
        'is_weekend': [0, 1, 0, 1],
        'is_night': [0, 1, 0, 1],
        'is_new_wallet': [0, 1, 0, 1],
        'chain_risk_score': [0, 1, 0, 1],
        'browser_risk_score': [0, 1, 0, 1],
        'transaction_amount': [100, 5000, 200, 10000],
        'wallet_age_days': [100, 5, 200, 3],
        'is_fraud': [0, 1, 0, 1]  # For training example
    })
    
    # Initialize detector
    detector = FraudDetector()
    
    # Train models
    detector.train(sample_data)
    
    # Make predictions
    results = detector.predict(sample_data)
    
    if results is not None:
        print("\nPrediction Results:")
        print(results[['fraud_probability', 'is_fraudulent', 'risk_factors']])
    
    # Example usage for TokenFraudDetector
    token_detector = TokenFraudDetector()
    
    # Example token address
    token_address = "0x123..."
    
    # Get risk report
    risk_report = token_detector.get_risk_report(token_address)
    
    # Print results
    print("\nRisk Analysis Report:")
    print(f"Token Address: {risk_report['token_address']}")
    print("\nRisk Scores:")
    for risk_type, score in risk_report['risk_scores'].items():
        print(f"{risk_type}: {score:.2f}")
    
    print("\nRecommendations:")
    for rec in risk_report['recommendations']:
        print(f"- {rec}")