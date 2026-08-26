from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "patient_events.csv"

event_log = pd.read_csv(DATA_PATH)

print(f"Total event rows: {len(event_log)}")
print(f"Total patients: {event_log['patient_id'].nunique()}")

print("\nEvents by type:")
print(event_log["event_name"].value_counts())

print("\nVisits by type:")
print(event_log["visit_type"].value_counts())

print("\nAverage wait time:")
print(f"{event_log['wait_minutes'].mean():.1f} minutes")

print("\nMissing values:")
print(event_log.isnull().sum())