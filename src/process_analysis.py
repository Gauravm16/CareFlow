import pandas as pd
import pm4py
from pm4py.algo.discovery.alpha import algorithm as alpha_miner


# 1. Load the XES event log
file_path = "data/raw/Sepsis Cases - Event Log.xes"
log = pm4py.read_xes(file_path)

#######################################################################
# 2. Create a clean event table

clean_log = log[
    [
        "case:concept:name",
        "concept:name",
        "time:timestamp",
        "org:group",
        "Age",
        "Diagnose",
        "InfectionSuspected",
        "Leucocytes",
        "CRP",
        "LacticAcid"
    ]
].copy()

clean_log.to_csv(
    "data/processed/clean_patient_events.csv",
    index=False
)

#######################################################################
# 3. Sort events by patient and time

events = log.sort_values(
    ["case:concept:name", "time:timestamp"]
).copy()

#######################################################################
# 4. Find the next activity for each patient

events["next_activity"] = (
    events.groupby("case:concept:name")["concept:name"]
    .shift(-1)
)

events["next_timestamp"] = (
    events.groupby("case:concept:name")["time:timestamp"]
    .shift(-1)
)

#######################################################################
# 5. Calculate waiting time between activities

events["waiting_minutes"] = (
    events["next_timestamp"] - events["time:timestamp"]
).dt.total_seconds() / 60

#######################################################################
# 6. Summarize process transitions

transitions = (
    events.dropna(subset=["next_activity", "waiting_minutes"])
    .groupby(["concept:name", "next_activity"])
    .agg(
        transition_count=("case:concept:name", "count"),
        average_wait_minutes=("waiting_minutes", "mean")
    )
    .reset_index()
    .sort_values("transition_count", ascending=False)
)

print("\nTop process transitions:")
print(transitions.head(20).to_string(index=False))

#######################################################################
# 7. Discover the process model using Alpha Miner

process_model = alpha_miner.apply(log)

print("\nProcess model discovered successfully.")
print(process_model)

#######################################################################
# 8. Save the process transitions to a CSV file
transitions.to_csv(
    "data/processed/process_transitions.csv",
    index=False
)