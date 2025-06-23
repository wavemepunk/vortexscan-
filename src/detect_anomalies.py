import os
from sklearn.preprocessing import LabelEncoder
import argparse
import pandas as pd
import joblib
import matplotlib.pyplot as plt  # Visualization
from datetime import datetime

os.makedirs("output", exist_ok=True)

# Baseline rules for known safe ranges (example values)
baseline_profiles = {
    "SAT001": {"temp_min": 10, "temp_max": 80, "voltage_min": 6, "voltage_max": 12},
    "SAT002": {"temp_min": 5, "temp_max": 75, "voltage_min": 5.5, "voltage_max": 11},
    "SAT003": {"temp_min": 0, "temp_max": 70, "voltage_min": 5, "voltage_max": 10},
}


def load_model(model_path="models/isolation_forest.pkl"):
    return joblib.load(model_path)

def load_data(data_path):
    data = pd.read_csv(data_path)
    # Optional: sort by time if needed
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    data = data.sort_values("timestamp")
    return data

    
def detect_anomalies(model, data):
    # Copy to avoid modifying original
    df = data.copy()

    # Label encode command_code if it exists
    if "command_code" in df.columns:
        le = LabelEncoder()
        df["command_code"] = le.fit_transform(df["command_code"])

    # Use only numeric features for prediction
    features = df.select_dtypes(include=["number"])

    # Predict anomalies
    predictions = model.predict(features)
    df["anomaly"] = predictions

    # ================================
    # ✅ Baseline Violation Detection
    # ================================
    df["baseline_violation"] = ""

    for sat_id, rules in baseline_profiles.items():
        mask = df["satellite_id"] == sat_id

        if "temperature" in df.columns:
            df.loc[mask & (df["temperature"] > rules["temp_max"]), "baseline_violation"] += "🔥 temp_high "
            df.loc[mask & (df["temperature"] < rules["temp_min"]), "baseline_violation"] += "❄️ temp_low "

        if "voltage" in df.columns:
            df.loc[mask & (df["voltage"] > rules["voltage_max"]), "baseline_violation"] += "🔌 voltage_high "
            df.loc[mask & (df["voltage"] < rules["voltage_min"]), "baseline_violation"] += "⚡ voltage_low "

    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect anomalies in satellite telemetry data.")
    parser.add_argument("--data", required=True, help="Path to the telemetry CSV file")
    args = parser.parse_args()

    # Load and process
    model = load_model()
    data = load_data(args.data)
    result = detect_anomalies(model, data)
    anomalies = result[result["anomaly"] == -1]

def tag_threats(row):
    if row["anomaly"] == -1:
        if row["baseline_violation"]:
            return f"🚨 Baseline Violation: {row['baseline_violation']}"
        elif row["command_code"] not in [0, 1, 2]:  # Replace with actual valid code indices
            return "⚠️ Suspicious Command Injection"
        elif row["temperature"] > 80:
            return "🔥 Overheat / Sensor Spoof"
        elif row["voltage"] < 3.0:
            return "🔌 Voltage Drop / Power Tampering"
        elif "02:00" <= row["timestamp"].strftime("%H:%M") <= "04:00":
            return "🕒 Odd-Time Command Execution"
        else:
            return "❓ Unknown Anomaly"
    return None

def check_baseline_violation(row):
    baseline = baseline_profiles.get(row["satellite_id"])
    if not baseline:
        return None  # Skip unknown satellites
    if row["temperature"] > baseline["temp_max"]:
        return "⚠️ Temp Exceeds Baseline"
    if row["voltage"] < baseline["voltage_min"]:
        return "⚠️ Voltage Below Baseline"
    return None


result["threat_tag"] = result.apply(tag_threats, axis=1)
result["baseline_violation"] = result.apply(check_baseline_violation, axis=1)

anomalies = result[result["anomaly"] == -1]


# Save all anomalies with tags
anomalies.to_csv("output/anomaly_report.csv", index=False)

    
# Save only the rows that violated baseline thresholds
violations = anomalies[anomalies["baseline_violation"].notnull()]
violations.to_csv("output/baseline_violations.csv", index=False)

print("[✓] Anomaly report saved to output/anomaly_report.csv")
print("[✓] Baseline violations saved to output/baseline_violations.csv")

print(f"\n[✓] Analysis complete. {len(anomalies)} anomalies found:\n")


# Safely check for column presence before printing
columns_to_show = ["timestamp", "satellite_id", "command_code", "temperature"]
available_columns = [col for col in columns_to_show if col in anomalies.columns]

print(anomalies[available_columns])



    
# Plot and save the anomaly graph

plt.figure(figsize=(10, 5))
plt.scatter(result["timestamp"], result["temperature"], label="Normal", alpha=0.6)


# Only plot if anomalies exist
if not anomalies.empty:
    plt.scatter(anomalies["timestamp"], anomalies["temperature"], color="red", label="Anomaly")


plt.scatter(anomalies["timestamp"], anomalies["temperature"], color="red", label="Anomaly")
plt.xlabel("Timestamp")
plt.ylabel("Temperature")
plt.title("Anomalies in Satellite Temperature")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("output/anomaly_plot.png")
plt.show()
print("[+] Plot saved to output/anomaly_plot.png")

# Save summary as .txt
print(f"\n[✓] Analysis complete. {len(anomalies)} anomalies found:\n")

# Safely check for column presence before printing
columns_to_show = ["timestamp", "satellite_id", "command_code", "temperature"]
available_columns = [col for col in columns_to_show if col in anomalies.columns]
print(anomalies[available_columns])

# Plot and save the anomaly graph
plt.figure(figsize=(10, 5))
plt.scatter(result["timestamp"], result["temperature"], label="Normal", alpha=0.6)

# Only plot anomalies if they exist
if not anomalies.empty:
    plt.scatter(anomalies["timestamp"], anomalies["temperature"], color="red", label="Anomaly")

plt.xlabel("Timestamp")
plt.ylabel("Temperature")
plt.title("Anomalies in Satellite Temperature")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("output/anomaly_plot.png")
plt.show()
print("[+] Plot saved to output/anomaly_plot.png")

# Save summary as .txt
with open("output/summary.txt", "w") as f:
    f.write(f"🛰️ VortexScan Report — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write(f"🔍 Total Anomalies Detected: {len(anomalies)}\n\n")
    if not anomalies.empty:
        for i, row in anomalies.iterrows():
            ts = row.get("timestamp", "N/A")
            sid = row.get("satellite_id", "N/A")
            cmd = row.get("command_code", "N/A")
            temp = row.get("temperature", "N/A")
            baseline = row.get("baseline_violation", "").strip()
            f.write(f"- [{ts}] Satellite {sid} | Command: {cmd} | Temp: {temp}° | Baseline: {baseline or 'None'}\n")
    else:
        f.write("No anomalies detected.\n")

print("[+] Summary saved to output/summary.txt")


# Per-satellite summary statistics (temp/voltage)
summary_stats = result.groupby("satellite_id")[["temperature", "voltage"]].describe()

# Save summary stats to CSV
# Save per-satellite summary stats to a CSV file
summary_stats.to_csv("output/per_satellite_summary.csv")
print("[+] Per-satellite stats saved to output/per_satellite_summary.csv")

