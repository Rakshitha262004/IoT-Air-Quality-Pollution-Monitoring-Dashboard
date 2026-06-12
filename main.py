"""
Main entry point for IoT Air Quality & Pollution Monitoring Dashboard
Run with: python main.py
"""

from python_simulation.simulate_air_quality import (
    run_simulation, generate_report, generate_chart
)

if __name__ == "__main__":
    print("=" * 50)
    print("IoT Air Quality & Pollution Monitoring Dashboard")
    print("Virtual Simulation Mode")
    print("=" * 50)

    run_simulation(
        cycles=20,
        delay_seconds=0.5,
        scenario_sequence=["normal", "moderate", "smoke", "hazardous"]
    )
    generate_report()
    generate_chart()

    print("\nDone! Check the 'data/' and 'outputs/' folders for results.")