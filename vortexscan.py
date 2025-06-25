import os
from tabulate import tabulate
import argparse
import joblib 
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from src.detect_anomalies2 import detect_anomalies

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

# Baseline definitions
baseline_profiles = {
    "SAT001": {"temp_min": 10, "temp_max": 80, "voltage_min": 6, "voltage_max": 12},
    "SAT002": {"temp_min": 5, "temp_max": 75, "voltage_min": 5.5, "voltage_max": 11},
    "SAT003": {"temp_min": 0, "temp_max": 70, "voltage_min": 5, "voltage_max": 10},
}

def load_model(model_path="models/isolation_forest.pkl"):
    return joblib.load(model_path)

def load_data(data_path):
    data = pd.read_csv(data_path)
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    return data.sort_values("timestamp")

def detect_anomalies(model, data):
    df = data.copy()
    if "command_code" in df.columns:
        df["command_code"] = LabelEncoder().fit_transform(df["command_code"])
    
    features = df[model.feature_names_in_]  # ✅ Match training

    df["anomaly"] = model.predict(features)
    df["baseline_violation"] = ""

    for sat_id, rules in baseline_profiles.items():
        mask = df["satellite_id"] == sat_id
        if "temperature" in df.columns:
            df.loc[mask & (df["temperature"] > rules["temp_max"]), "baseline_violation"] += "temp_high "
            df.loc[mask & (df["temperature"] < rules["temp_min"]), "baseline_violation"] += "temp_low "
        if "voltage" in df.columns:
            df.loc[mask & (df["voltage"] > rules["voltage_max"]), "baseline_violation"] += "voltage_high "
            df.loc[mask & (df["voltage"] < rules["voltage_min"]), "baseline_violation"] += "voltage_low "
    return df


def tag_threats(row):
    if row["anomaly"] == -1:
        tags = []

        # Add detailed baseline violations
        if row["baseline_violation"]:
            if "temp_high" in row["baseline_violation"]:
                tags.append("Temperature Too High")
            if "temp_low" in row["baseline_violation"]:
                tags.append("Temperature Too Low")
            if "voltage_high" in row["baseline_violation"]:
                tags.append("Voltage Too High")
            if "voltage_low" in row["baseline_violation"]:
                tags.append("Voltage Too Low")

        # Other threat indicators
        if row.get("command_code") not in [0, 1, 2]:
            tags.append("Suspicious Command Injection")
        if row.get("temperature", 0) > 80:
            tags.append("Overheat / Sensor Spoof")
        if row.get("voltage", 10) < 3.0:
            tags.append("Power Tampering")
        if "02:00" <= row["timestamp"].strftime("%H:%M") <= "04:00":
            tags.append("Odd-Time Command Execution")

        return " | ".join(tags) if tags else "Unknown Anomaly"
    return None

      
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect anomalies in satellite telemetry data")
    parser.add_argument("--data", required=True, help="Path to telemetry CSV")
    args = parser.parse_args()

    model = load_model()
    data = load_data(args.data)

    # Save feature names to avoid mismatch during prediction
    model.feature_names_in_ = ["temperature", "voltage", "signal_strength", "command_code"]

    # Run anomaly detection
    result = detect_anomalies(model, data)

    # Tag cyber threat types
    result["threat_tag"] = result.apply(tag_threats, axis=1)

    # Extract anomalies
    anomalies = result[result["anomaly"] == -1]

    # Save reports
    anomalies.to_csv("output/anomaly_report.csv", index=False)
    violations = anomalies[anomalies["baseline_violation"].notnull()]
    violations.to_csv("output/baseline_violations.csv", index=False)

    # Optional: Show output in console
    pd.set_option("display.max_rows", None)
    print("\n🔍 Detected Anomalies:\n")
    print(tabulate(
    anomalies[["timestamp", "satellite_id", "temperature", "voltage", "baseline_violation", "threat_tag"]],
    headers='keys',
    tablefmt='fancy_grid',
    showindex=False
))


# Optional: Save pretty table to text file for reports
with open("output/anomaly_report.txt", "w") as f:
    f.write(tabulate(
        anomalies[["timestamp", "satellite_id", "temperature", "voltage", "baseline_violation", "threat_tag"]],
        headers='keys',
        tablefmt='grid',
        showindex=False
    ))


    # Plot
    plt.figure(figsize=(10, 5))
    plt.scatter(result["timestamp"], result["temperature"], label="Normal", alpha=0.6)
    if not anomalies.empty:
        plt.scatter(anomalies["timestamp"], anomalies["temperature"], color="red", label="Anomaly")
    plt.xlabel("Timestamp")
    plt.ylabel("Temperature")
    plt.title("Anomalies in Satellite Temperature")
    plt.legend()
    plt.tight_layout()
    plt.savefig("output/anomaly_plot.png")
    plt.show()
    print("[+] Plot saved to output/anomaly_plot.png")

    # Save summary text
    with open("output/summary.txt", "w") as f:
        f.write(f"🛰️ VortexScan Report — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"🔍 Total Anomalies Detected: {len(anomalies)}\n\n")
        if not anomalies.empty:
            for _, row in anomalies.iterrows():
                ts = row.get("timestamp", "N/A")
                sid = row.get("satellite_id", "N/A")
                cmd = row.get("command_code", "N/A")
                temp = row.get("temperature", "N/A")
                baseline = row.get("baseline_violation", "").strip()
                f.write(f"- [{ts}] Satellite {sid} | Command: {cmd} | Temp: {temp}° | Baseline: {baseline or 'None'}\n")
        else:
            f.write("No anomalies detected.\n")
    print("[+] Summary saved to output/summary.txt")

    # Per-satellite stats
    summary_stats = result.groupby("satellite_id")[["temperature", "voltage"]].describe()
    summary_stats.to_csv("output/per_satellite_summary.csv")
    print("[+] Per-satellite stats saved to output/per_satellite_summary.csv")
