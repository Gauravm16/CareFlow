import pm4py

file_path = "data/raw/Sepsis Cases - Event Log.xes"

log = pm4py.read_xes(file_path) # Reading the XES event log file
#######################################################################
# Analyzing the total number of events in the log

print("Total events:", len(log))

#######################################################################
# Analyzing the columns in the event log

print("\nColumns:")
print(log.columns.tolist())

#######################################################################
# Analyzing the first 5 events

print("\nFirst 5 events:")
print(log.head())

