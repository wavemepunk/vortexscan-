import json
import pandas as pd
import joblib

# Load the trained model
MODEL_PATH = "models/isolation_forest.pkl"
model = joblib.load(MODEL_PATH)

# Load baseline profiles
with open("data/baseline_profiles.json") as f:
    baseline_profiles = json.load(f)

def check_baseline_rules(row):
    violations = []
    cmd = str(int(row["command_code"]))  # convert float to str safely
    if cmd in baseline_profiles:
        profile = baseline_profiles[cmd]
        for key in ["temperature", "voltage", "signal_strength"]:
            val = row[key]
            rule = profile.get(key, {})
            if not (rule["min"] <= val <= rule["max"]):
                violations.append(f"{key} out of range ({val} not in {rule})")
    return violations

def detect_anomalies(df):
    results = []
    features = df[["temperature", "voltage", "command_code", "signal_strength"]]
    preds = model.predict(features)
    scores = model.decision_function(features)

    for i, row in df.iterrows():
        label = "Anomaly" if preds[i] == -1 else "Normal"
        score = scores[i]
        baseline_violations = check_baseline_rules(row)
        results.append({
            "timestamp": row["timestamp"],
            "label": label,
            "anomaly_score": round(score, 3),
            "baseline_violations": baseline_violations
        })
    return results
