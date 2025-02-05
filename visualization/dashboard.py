import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

class FraudDashboard:
    def __init__(self, df):
        self.df = df

    def run(self):
        st.set_page_config(page_title="Crypto Fraud Detection", layout="wide")
        
        st.title("🔍 Cryptocurrency Fraud Detection Dashboard")
        
        # Sidebar filters
        st.sidebar.title("Filters")
        selected_chain = st.sidebar.multiselect(
            "Select Blockchain",
            options=self.df['blockchain'].unique()
        )
        
        # Filter data based on selection
        if selected_chain:
            filtered_df = self.df[self.df['blockchain'].isin(selected_chain)]
        else:
            filtered_df = self.df

        # Layout with columns
        col1, col2 = st.columns(2)
        
        with col1:
            self._plot_fraud_distribution(filtered_df)
        
        with col2:
            self._plot_risk_factors(filtered_df)
        
        # Transaction patterns over time
        st.subheader("Transaction Patterns Over Time")
        self._plot_transaction_patterns(filtered_df)
        
        # High-risk wallets table
        st.subheader("High-Risk Wallets")
        self._display_high_risk_wallets(filtered_df)

    def _plot_fraud_distribution(self, df):
        fig = px.histogram(
            df,
            x='fraud_probability',
            title='Distribution of Fraud Probability Scores',
            nbins=50
        )
        st.plotly_chart(fig)

    def _plot_risk_factors(self, df):
        risk_factors = {
            'High Frequency Trading': 'is_high_frequency',
            'Suspicious Hours': 'is_suspicious_hour',
            'High-Risk Chain': 'is_high_risk_chain',
            'Amount Outliers': 'is_outlier_amount'
        }
        
        risk_counts = {name: df[col].sum() for name, col in risk_factors.items()}
        
        fig = px.bar(
            x=list(risk_counts.keys()),
            y=list(risk_counts.values()),
            title='Risk Factor Distribution'
        )
        st.plotly_chart(fig)

    def _plot_transaction_patterns(self, df):
        daily_patterns = df.groupby(df['timestamp'].dt.date).agg({
            'transaction_amount': 'sum',
            'fraud_probability': 'mean'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_patterns['timestamp'],
            y=daily_patterns['transaction_amount'],
            name='Transaction Volume'
        ))
        fig.add_trace(go.Scatter(
            x=daily_patterns['timestamp'],
            y=daily_patterns['fraud_probability'],
            name='Avg Fraud Probability',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='Daily Transaction Volume vs Fraud Probability',
            yaxis2=dict(overlaying='y', side='right')
        )
        
        st.plotly_chart(fig)

    def _display_high_risk_wallets(self, df):
        high_risk = df[df['fraud_probability'] > 0.8].groupby('wallet_address').agg({
            'transaction_amount': 'sum',
            'fraud_probability': 'mean',
            'blockchain': 'first',
            'daily_tx_count': 'max'
        }).reset_index()
        
        high_risk = high_risk.sort_values('fraud_probability', ascending=False)
        st.dataframe(high_risk)

if __name__ == "__main__":
    # Initialize processor
    processor = DataProcessor()
    
    # Load and process data
    df = processor.load_data("path_to_your_data.csv")
    df = processor.engineer_features(df)
    
    # Train model
    model = FraudDetectionModel()
    X, y = model.prepare_features(df)
    model.train(X, y)
    
    # Add fraud probabilities to DataFrame
    df['fraud_probability'] = model.predict(X)
    
    # Launch dashboard
    dashboard = FraudDashboard(df)
    dashboard.run()