from datetime import datetime, timedelta
from pathlib import Path
import random

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "patient_events.csv"

random.seed(42)

events = []

for patient_number in range(1, 1001):
    patient__id = f"p{patient_number:03d}"

    visit_type = random.choice(["Emergency", "Routine"])
    priority = "High" if visit_type == "Emergency" else "low"

    arrival_time = datetime(2026, 1, 1) + timedelta(days=random.randint(0, 89), minutes=random.randint(0, 1439))

    if visit_type == "Emergency":
        journey = [
            ("Registration", "Reception"),
            ("Assessment","Emergency"),
            ("Consultation", "Emergency"),
            ("Treatment", "Emergency"),
            ("Discharge", "Reception"),
        ]
    else:  
        journey = [
            ("Registration", "Reception"),
            ("Consultation", "Clinic"),
            ("Lab Test", "Laboratory"),
            ("Follow-up", "Clinic"),
            ("Discharge", "Reception"),
        ]

    current_time = arrival_time

    for event_name, department in journey:
        wait_minutes = random.randint(5, 45)  # Random wait time between 5 and 45 minutes
        current_time += timedelta(minutes=wait_minutes)

        events.append(
            {
            "patient_id": patient__id,
            "event_name": event_name,
            "event_time": current_time,
            "department": department,
            "visit_type": visit_type,
            "priority": priority,
            "wait_minutes": wait_minutes,
            }
        )

    event_log = pd.DataFrame(events).sort_values(["patient_id", "event_time"])
event_log.to_csv(RAW_DATA_PATH, index=False)

print(f"Created {len(event_log)} events for 1000 patients.")
print(f"Data saved to {RAW_DATA_PATH}")