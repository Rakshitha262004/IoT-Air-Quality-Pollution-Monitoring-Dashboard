"""
IoT Air Quality & Pollution Monitoring Dashboard
Python Virtual Simulation
-------------------------------------------------
Simulates MQ135 (air quality) and DHT11 (temp/humidity)
sensor readings, classifies pollution level, triggers
alerts, logs data to CSV, and generates charts.
"""

import random
import csv
import os
import time
from datetime import datetime
import matplotlib.pyplot as plt

# ---------- CONFIG ----------
LOG_FILE = "data/air_quality_log.csv"
REPORT_FILE = "outputs/sample_report.txt"
CHART_FILE = "outputs/air_quality_chart.png"

AQI_GOOD_MAX = 1000
AQI_MODERATE_MAX = 2000
AQI_POOR_MAX = 3000

SIMULATION_SCENARIOS = ["normal", "moderate", "smoke", "hazardous"]


def simulate_mq135(scenario="normal"):
    """Generate a simulated MQ135 ADC value based on scenario."""
    ranges = {
        "normal":    (200, 1000),
        "moderate":  (1001, 2000),
        "smoke":     (2001, 3000),
        "hazardous": (3001, 4095),
    }
    low, high = ranges.get(scenario, ranges["normal"])
    return random.randint(low, high)


def simulate_dht11(scenario="normal"):
    """Generate simulated temperature and humidity."""
    base_temp = random.uniform(24, 32)
    base_humidity = random.uniform(40, 70)

    if scenario in ("smoke", "hazardous"):
        base_temp += random.uniform(2, 5)  # heat from smoke/fire scenario

    return round(base_temp, 1), round(base_humidity, 1)


def classify_air_quality(mq135_value):
    """Classify pollution level based on MQ135 reading."""
    if mq135_value <= AQI_GOOD_MAX:
        return "Good"
    elif mq135_value <= AQI_MODERATE_MAX:
        return "Moderate"
    elif mq135_value <= AQI_POOR_MAX:
        return "Poor"
    else:
        return "Hazardous"


def generate_alert(status):
    """Return alert message based on status."""
    alerts = {
        "Good": "Air quality is GOOD. No action needed.",
        "Moderate": "Air quality is MODERATE. Sensitive groups should limit exposure.",
        "Poor": "WARNING: Air quality is POOR. Reduce outdoor activity.",
        "Hazardous": "ALERT! HAZARDOUS air quality detected! Take immediate precautions.",
    }
    return alerts.get(status, "Unknown status")


def init_log_file():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "mq135_value", "temperature_C",
                              "humidity_%", "status", "alert"])


def log_reading(timestamp, mq135_value, temp, humidity, status, alert):
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, mq135_value, temp, humidity, status, alert])


def run_simulation(cycles=10, delay_seconds=1, scenario_sequence=None):
    """
    Run the simulation for a given number of cycles.
    scenario_sequence: optional list of scenarios to cycle through,
                        otherwise random scenarios are used.
    """
    init_log_file()
    print("Starting IoT Air Quality Monitoring Simulation...\n")

    for i in range(cycles):
        scenario = (scenario_sequence[i % len(scenario_sequence)]
                    if scenario_sequence else random.choice(SIMULATION_SCENARIOS))

        mq135_value = simulate_mq135(scenario)
        temp, humidity = simulate_dht11(scenario)
        status = classify_air_quality(mq135_value)
        alert = generate_alert(status)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"[{timestamp}] Scenario: {scenario.upper()}")
        print(f"  MQ135 Value : {mq135_value}")
        print(f"  Temperature : {temp} C")
        print(f"  Humidity    : {humidity} %")
        print(f"  Air Quality : {status}")
        print(f"  Alert       : {alert}")
        print("-" * 50)

        log_reading(timestamp, mq135_value, temp, humidity, status, alert)
        time.sleep(delay_seconds)

    print("\nSimulation complete. Data logged to:", LOG_FILE)


def generate_report():
    """Generate a text summary report from the CSV log."""
    if not os.path.exists(LOG_FILE):
        print("No log file found. Run simulation first.")
        return

    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)

    with open(LOG_FILE, "r") as f:
        reader = list(csv.DictReader(f))

    if not reader:
        print("Log file is empty.")
        return

    total = len(reader)
    status_counts = {}
    for row in reader:
        status_counts[row["status"]] = status_counts.get(row["status"], 0) + 1

    with open(REPORT_FILE, "w") as f:
        f.write("AIR QUALITY MONITORING REPORT\n")
        f.write("=" * 40 + "\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total readings: {total}\n\n")
        f.write("Status Distribution:\n")
        for status, count in status_counts.items():
            percentage = (count / total) * 100
            f.write(f"  {status:10s}: {count:3d} readings ({percentage:.1f}%)\n")
        f.write("\nLatest Reading:\n")
        last = reader[-1]
        for key, value in last.items():
            f.write(f"  {key}: {value}\n")

    print("Report generated:", REPORT_FILE)


def generate_chart():
    """Generate a chart of MQ135 values over time from the CSV log."""
    if not os.path.exists(LOG_FILE):
        print("No log file found. Run simulation first.")
        return

    os.makedirs(os.path.dirname(CHART_FILE), exist_ok=True)

    timestamps, mq135_values, temps, humidities = [], [], [], []
    with open(LOG_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            timestamps.append(row["timestamp"])
            mq135_values.append(int(row["mq135_value"]))
            temps.append(float(row["temperature_C"]))
            humidities.append(float(row["humidity_%"]))

    fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    axs[0].plot(mq135_values, color="red", marker="o")
    axs[0].set_title("Air Quality (MQ135 ADC Value)")
    axs[0].axhline(y=AQI_GOOD_MAX, color="green", linestyle="--", label="Good limit")
    axs[0].axhline(y=AQI_MODERATE_MAX, color="orange", linestyle="--", label="Moderate limit")
    axs[0].axhline(y=AQI_POOR_MAX, color="red", linestyle="--", label="Poor limit")
    axs[0].legend()

    axs[1].plot(temps, color="orange", marker="o")
    axs[1].set_title("Temperature (C)")

    axs[2].plot(humidities, color="blue", marker="o")
    axs[2].set_title("Humidity (%)")
    axs[2].set_xlabel("Reading Index")

    plt.tight_layout()
    plt.savefig(CHART_FILE)
    print("Chart saved:", CHART_FILE)


if __name__ == "__main__":
    # Run a scripted scenario sequence covering all pollution levels
    run_simulation(
        cycles=20,
        delay_seconds=0.5,
        scenario_sequence=["normal", "moderate", "smoke", "hazardous"]
    )
    generate_report()
    generate_chart()