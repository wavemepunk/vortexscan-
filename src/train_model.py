import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

def train_model(input_csv="data/telemetry_realistic.csv", output_model="models/isolation_forest.pkl"):
    df = pd.read_csv(input_csv)

    # Encode command_code (non-numeric)
    df['command_code'] = df['command_code'].astype('category').cat.codes

    # Drop non-feature columns
    features = df[['temperature', 'voltage', 'command_code', 'signal_strength']]
    print("Training features:", list(features.columns))

    # Train model
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(features)

    # Save the model
    joblib.dump(model, output_model)
    print(f"[✓] Model trained and saved to {output_model}")

if __name__ == "__main__":
    train_model()
