import pandas as pd
import random
from datetime import datetime, timedelta

def generate_telemetry_data(filename="data/telemetry_sample.csv", num_rows=500):
    satellite_ids = ['SAT001', 'SAT002', 'SAT003']
    command_codes = ['CMD_001', 'CMD_002', 'CMD_003', 'CMD_004', 'CMD_005']
    data = []

    current_time = datetime.now()

    for _ in range(num_rows):
        sat_id = random.choice(satellite_ids)
        temperature = round(random.uniform(20, 90), 2)
        voltage = round(random.uniform(3.0, 15.0), 2)
        command = random.choice(command_codes)
        signal = round(random.uniform(50, 100), 2)

        # Inject 5% anomalies
        if random.random() < 0.05:
            temperature = round(random.uniform(100, 150), 2)  # High temp anomaly
            voltage = round(random.uniform(0.1, 2.0), 2)       # Low voltage
            command = 'CMD_X99'                                 # Spoofed command
            signal = round(random.uniform(0, 10), 2)            # Signal drop

        data.append([
            current_time.strftime("%Y-%m-%d %H:%M:%S"),
            sat_id, temperature, voltage, command, signal
        ])
        current_time += timedelta(seconds=5)

    df = pd.DataFrame(data, columns=[
        'timestamp', 'satellite_id', 'temperature',
        'voltage', 'command_code', 'signal_strength'
    ])
    df.to_csv(filename, index=False)
    print(f"[✓] Generated {num_rows} telemetry rows to {filename}")

if __name__ == "__main__":
    generate_telemetry_data()
