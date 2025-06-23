# 🚀 VortexScan: AI-Powered Satellite Telemetry Anomaly Detection

**For Bhartiya Antariksh Hackathon 2025**  
Detect cyber threats and anomalies in satellite telemetry using AI + baseline rules.

---

## 📌 Project Summary

**VortexScan** is a Python-based anomaly detection tool designed to analyze satellite telemetry data (e.g., temperature, voltage) and detect unusual behaviors that may indicate cyberattacks, faults, or unknown anomalies. It combines:

- 🧠 Isolation Forest (Unsupervised ML) to detect unknown anomalies  
- 🔍 Baseline Rule Violation Engine for known “safe” ranges per satellite  
- 🏷️ Threat Tagging System to identify suspicious cyber activity  
- 📈 Data Visualization with Matplotlib  
- 📄 CSV Reports for actionable output and review  

---

## 📂 Folder Structure


vortexscan-/
├── data/
│ ├── telemetry_realistic.csv # Input satellite telemetry
│ └── baseline_profiles.json # Safe thresholds per satellite
├── models/
│ └── isolation_forest.pkl # Trained ML model
├── output/
│ ├── anomaly_report.csv # Final flagged anomaly records
│ ├── anomaly_report.txt # Pretty printable version
│ ├── baseline_violations.csv # Known rule violations
│ ├── per_satellite_summary.csv # Summary view per satellite
│ ├── summary.txt # Human-readable highlights
│ └── anomaly_plot.png # Graph of detected anomalies
├── src/
│ ├── detect_anomalies.py # Core detection logic
│ ├── train_model.py # Isolation Forest training
│ └── data_generator.py # Simulate or format telemetry
├── vortexscan.py # Main CLI entrypoint
├── anomaly_plot.png # Copy of graph output
├── README.md # This file
├── requirements.txt # Dependencies
└── summary.txt # Final summary report


---

## ✅ Features

- 📊 Real-time anomaly detection using AI  
- 🧾 Clean, readable CSV output (with anomaly flags & threat tags)  
- 🔐 Baseline rule checks for satellite health deviations  
- 🚀 Cyber threat tagging (e.g., command injection, voltage manipulation)  
- 📈 Optional time-series visualization of anomalies  

---

## 🛠️ Installation / Setup

```bash
# Clone the repo
git clone https://github.com/wavemepunk/vortexscan-.git
cd vortexscan-

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

▶️ Usage

# Run the analysis
python3 vortexscan.py --data data/telemetry_realistic.csv

📊 Sample Output

timestamp           | satellite_id | temperature | voltage | baseline_violation | threat_tag
------------------- | ------------ | ----------- | ------- | ------------------ | -------------------------
2025-06-21 22:00:00 | SAT003       | 32.31       | 8.28    |                    | Suspicious Command Injection
2025-06-21 21:30:00 | SAT002       | 30.56       | 8.69    |                    | Unknown Anomaly
2025-06-21 03:00:00 | SAT002       | -13.42      | 6.83    | temp_low           | Temperature Too Low

💻 Tech Stack

    Python 3.10+

    pandas, scikit-learn, matplotlib

    JSON-based config for thresholds

    CSV input/output pipeline

🎯 Use Case

This tool helps satellite operators, analysts, and defense teams:

    Detect potential cyberattacks like spoofed commands or voltage tampering

    Identify unknown anomalies in real-time

    Quickly scan logs for early warnings

🧠 Future Improvements

    Live telemetry stream analysis

    Integration with C2 or alerting systems

    Web-based GUI (Streamlit)

👥 Team

    👩‍💻 Leader: Roshni Nai

    🧑‍💻 Member 2: Bihag Parihar

    🧑‍💻 Member 3: Krish Singh

    🛰️ Hackathon: Bhartiya Antariksh Hackathon 2025

    🏫 Institute: Hansaba College of Engineering and Technology

🏁 Status

✅ MVP complete and tested
📦 Ready for submission
🌐 Upload to GitHub recommended
📜 License & Credit

Made with ❤️ for Bhartiya Antariksh Hackathon 2025
Developed by Roshni Nai
