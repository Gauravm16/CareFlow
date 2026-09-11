CareFlow — Clinical Pathway Process Mining & Analytics
1. Project Overview
CareFlow is a healthcare process analytics project designed to analyse patient journeys through a hospital emergency-care pathway.
Traditional dashboards can show metrics such as average waiting time and number of patients, but they do not always show how patients actually move through a process. CareFlow uses process mining to analyse the sequence of activities recorded for each patient case and identify variations, repeated activities, waiting times, and possible process inefficiencies.
The project uses the public Sepsis Cases – Event Log dataset containing approximately 1,050 patient cases and 15,214 events.
2. Problem Statement
Hospital administrators need to understand why patients may experience long waiting times or follow different treatment pathways.
A conventional BI dashboard can show an average waiting time, but it does not clearly answer questions such as:
- What activities usually happen first?
- Where do patients wait between activities?
- Which activities are repeated?
- Do patients return to the emergency department?
- How different are patient pathways?
CareFlow addresses this by combining process mining, data transformation, cloud data warehousing, and business intelligence.
3. Project Objectives
The main objectives are:
1. Analyse real patient event-log data.
2. Clean and structure the event data for analysis.
3. Calculate transitions and waiting times between activities.
4. Discover the underlying process using process-mining techniques.
5. Create analytical models using dbt.
6. Store and query the transformed data using BigQuery.
7. Build an interactive Power BI dashboard.
8. Provide useful information about patient pathways and hospital operations.
4. Dataset
The project uses the public Sepsis Cases – Event Log dataset.
Source: 4TU.ResearchData
Format: XES (eXtensible Event Stream)
The dataset contains:
- 1,050 cases
- 15,214 events
- 16 unique activities
The dataset is anonymized and represents hospital patient-care processes.
Main event-log concepts
Concept	Meaning
Case ID	Identifies an individual patient case
Activity	An action performed during the patient's journey
Timestamp	Time at which the activity occurred
Department/Group	Organizational group associated with an event


Examples of activities include:
- ER Registration
- ER Triage
- ER Sepsis Triage
- Leucocytes
- CRP
- LacticAcid
- IV Liquid
- IV Antibiotics
- Admission NC
- Return ER
- Release A/B/C/D/E
5. Initial Synthetic Data Attempt
An initial attempt was made to create synthetic patient-event data using Python so that the complete pipeline could be developed from generated data.
However, the synthetic-data approach did not work reliably enough for the intended process-mining analysis. The project was therefore reset and the synthetic data approach was abandoned.
The final implementation uses the public Sepsis Cases event log, providing real event sequences for process analysis.
6. Project Architecture
The final project follows this pipeline:
Sepsis XES Event Log
        ↓
Python + pandas + PM4Py
        ↓
Clean Patient Events
        ↓
Process Transition Analysis
        ↓
BigQuery
        ↓
dbt Transformations
        ↓
3 Analytical Models
        ↓
Power BI Dashboard
The three dbt models are:
stg_patient_events
        ↓
patient_journey_summary
        ↓
kpi_summary
7. Python Data Processing
Python was used as the main data-processing and process-mining language.
The main libraries were:
- pandas — data manipulation and analysis
- PM4Py — process mining
- Jupyter — interactive data analysis
7.1 Loading the XES file
PM4Py was used to read the event log:
log = pm4py.read_xes(file_path)
This loads the XES event log into a pandas-style data structure.
7.2 Creating the clean event table
Only the relevant fields were selected:
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
The cleaned data was saved as:
data/processed/clean_patient_events.csv
This creates a simpler dataset for downstream analysis.
8. Patient Event Ordering
Patient events were sorted by:
1. Case ID
2. Timestamp
events = log.sort_values(
    ["case:concept:name", "time:timestamp"]
).copy()
This is important because process mining depends on knowing the actual order of activities.
9. Finding the Next Activity
The next activity for each patient was identified using:
events["next_activity"] = (
    events.groupby("case:concept:name")["concept:name"]
    .shift(-1)
)
What this means
groupby() separates events by patient.
shift(-1) moves the next event into the current row.
For example:
ER Registration → ER Triage → ER Sepsis Triage
becomes:
Activity	Next Activity
ER Registration	ER Triage
ER Triage	ER Sepsis Triage
ER Sepsis Triage	next activity


This allows transitions to be analysed.
10. Waiting-Time Calculation
The next timestamp was also identified:
events["next_timestamp"] = (
    events.groupby("case:concept:name")["time:timestamp"]
    .shift(-1)
)
The waiting time was then calculated:
events["waiting_minutes"] = (
    events["next_timestamp"] - events["time:timestamp"]
).dt.total_seconds() / 60
This calculates the time between one activity and the next activity in minutes.
11. Process Transition Analysis
Transitions were grouped and summarized:
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
Two important metrics were produced:
Transition count
How many times a particular activity-to-activity transition occurred.
Average waiting time
The average time between the two activities.
The results were saved as:
data/processed/process_transitions.csv
12. Process Discovery
PM4Py's Alpha Miner was used to discover a process model:
process_model = alpha_miner.apply(log)
The Alpha Miner analyses the event log and attempts to discover relationships between activities.
This helps move from simply looking at individual rows of data to understanding the overall process structure.
13. BigQuery
Google BigQuery was used as the cloud data warehouse.
The project uses:
Project: careflow-analytics-506719
Dataset: careflow_raw
The cleaned patient-event data was loaded into BigQuery as:
patient_events_clean
The data contains 15,214 events.
BigQuery was selected because it provides a convenient environment for storing and querying analytical data using SQL.
14. dbt
dbt (data build tool) was used to transform the BigQuery data into structured analytical models.
The project contains exactly three dbt models.
14.1 stg_patient_events
This is the staging model.
Its main purpose is to rename technical event-log fields into easier analytical names.
For example:
case:concept:name → case_id
concept:name → activity
time:timestamp → event_timestamp
org:group → department
This makes the data easier to understand and use downstream.
14.2 patient_journey_summary
This model creates one summary record per patient case.
It calculates:
- First event time
- ER registration time
- Admission time
- Release time
- Total number of events
- ER return count
- Age
- Diagnosis
- Infection status
- ER-to-admission duration
- Admission-to-release duration
For example:
TIMESTAMP_DIFF(
    admission_time,
    er_registration_time,
    MINUTE
)
calculates the time between ER registration and admission in minutes.
14.3 kpi_summary
This model produces overall project KPIs.
It calculates:
- Total patients
- Total admissions
- Total releases
- Patients with ER return
- Average ER waiting time
- Average hospital stay
- Total events
The model uses functions such as:
COUNT()
COUNTIF()
AVG()
SUM()
ROUND()
15. Data Quality Checks
A quality check was performed on the patient journey summary.
The results were:
Metric	Result
Total patients	1,050
Negative admission times	0
Missing admission times	250
Negative stay times	0
Missing stay times	275


Interpretation
There were no negative durations, which indicates that the calculated time intervals were logically valid.
Missing admission or release information was not automatically treated as an error.
Some patient cases simply do not contain the required event for calculating a particular duration. These cases should not be incorrectly converted to zero or deleted without justification.
16. Power BI Dashboard
Power BI was used to create the final analytical dashboard.
The dashboard contains two pages.
Page 1 — CareFlow Overview
Main title
CareFlow
Subtitle
Clinical Pathway Process Mining & Analytics
KPI cards
1. Total Patients — 1,050
2. Total Events — 15,214
3. Total Admissions — 800
4. Patients with ER Return — 294
5. Avg ER Wait (min) — 460.08
6. Avg Hospital Stay (hrs) — 177.22
Activity Frequency
A bar chart showing how frequently different activities occur in the event log.
This helps identify the most frequently recorded activities.
ER Returns
A donut chart showing patient cases according to their ER-return status.
This helps highlight cases involving emergency-department return events.
17. Page 2 — Process Analysis
Subtitle
Patient pathway and waiting-time analysis
The page contains four main visuals.
17.1 Process Transitions
A grouped bar chart showing relationships between current activities and their next activities.
It provides a visual view of how patients move between activities.
17.2 Average Waiting Time (min)
This visual shows waiting-time information associated with process transitions.
It helps identify transitions where more time is spent between activities.
17.3 Hospital Stay Distribution
A column chart showing the distribution of hospital-stay duration using 24-hour bins.
This helps show how patient stays are distributed rather than relying only on the overall average.
17.4 ER Wait by Age
A line chart showing average ER-to-admission time across patient ages.
This shows variation in waiting time across age groups.
Important limitation: this visual shows association/variation, not causation. It cannot prove that age causes longer or shorter waiting times.
18. Key Process Observations
The event log shows substantial variation in patient pathways.
Examples of observed sequences include:
ER Registration
→ ER Triage
→ ER Sepsis Triage
and longer pathways such as:
ER Registration
→ ER Triage
→ ER Sepsis Triage
→ CRP
→ LacticAcid
→ Leucocytes
→ IV Liquid
→ IV Antibiotics
Some activities are also repeated during a patient's journey, particularly laboratory monitoring.
The analysis therefore demonstrates why event-log analysis can provide information that a simple patient-count dashboard cannot.
19. Important Methodological Limitation
Not every long transition time represents an emergency-department bottleneck.
For example, a patient may spend many hours or days in the hospital between recorded activities because of inpatient monitoring.
Therefore, a large waiting-time value should not automatically be interpreted as an ER bottleneck.
Process-mining results should be interpreted in the context of the actual patient journey and the meaning of each activity.
20. Challenges Encountered
Several technical issues were encountered during development.
Synthetic data approach
The initial synthetic-data approach was not reliable enough, so it was replaced with the public Sepsis event log.
BigQuery
The project initially contained an earlier synthetic-data table. It was removed during the project reset before loading the final dataset.
Python environment
A virtual environment was created to keep the project's Python dependencies separate.
BigQuery command-line path
The Google Cloud CLI initially was not available directly in the VS Code terminal. The Google Cloud SDK path was added to the environment.
dbt working directory
dbt commands initially required running from the correct dbt project directory.
SQL editor
The VS Code SQL parser was initially configured for a different SQL dialect, which caused misleading syntax highlighting. The actual SQL was intended for BigQuery.
Incomplete patient journeys
Some cases do not contain admission or release events. These were preserved rather than incorrectly treating missing values as zero.
21. Git and Version Control
GitHub was used for version control.
The working branch is:
gaurav-work
The main branch was kept untouched.
The project was committed in two major stages:
Commit 1
Replace synthetic data with Sepsis event log and complete pipeline
This captured the transition from the earlier synthetic-data attempt to the final Sepsis-based pipeline.
Commit 2
Add Power BI dashboard for Sepsis event log data
This added the final Power BI dashboard:
dashboard/CareFlow_Dashboard.pbix
22. Use of ChatGPT
ChatGPT was used as a learning and reference aid during development.
Its use was mainly for:
- understanding unfamiliar process-mining concepts
- learning Python syntax and methods
- understanding data-analysis techniques
- understanding the structure of the data pipeline
- troubleshooting development issues
The project was implemented, tested, and reviewed by the student. ChatGPT was not treated as a replacement for understanding the implementation.
23. Tools and Technologies
Technology	Purpose
Python	Data processing and analysis
pandas	Data manipulation
PM4Py	Process mining
XES	Event-log data format
BigQuery	Cloud data warehouse
SQL	Data transformation and analysis
dbt	Data transformation and modelling
Power BI	Dashboard and visualization
Git	Version control
GitHub	Repository hosting
VS Code	Development environment


24. Final Project Flow
Public Sepsis Event Log
        │
        ▼
      XES Data
        │
        ▼
 Python + PM4Py + pandas
        │
        ├──────────────► Clean Patient Events CSV
        │
        └──────────────► Process Transitions CSV
                              │
                              ▼
                         BigQuery
                              │
                              ▼
                            dbt
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
    stg_patient_events   patient_journey_summary   kpi_summary
             │                │                │
             └────────────────┼────────────────┘
                              ▼
                         Power BI
                              │
                              ▼
                    CareFlow Dashboard
25. Future Improvements
Possible future improvements include:
- More detailed conformance checking
- More rigorous bottleneck identification
- Additional process-mining algorithms
- Automated data refresh
- More detailed patient-pathway drilldowns
- Statistical analysis of factors associated with waiting time
- A completely offline version of the dashboard and analytical pipeline
26. Conclusion
CareFlow demonstrates how process mining can be combined with modern data-analytics technologies to analyse healthcare processes.
The project transforms a real event log into meaningful analytical information through:
Python → PM4Py → BigQuery → dbt → Power BI
The final dashboard provides both high-level KPIs and process-level information, allowing patient pathways, activity frequencies, transitions, waiting times, hospital stays, and ER returns to be explored from multiple perspectives.
The project also provided practical experience with event-log data, process mining, SQL transformation, cloud data warehousing, dashboard development, and version control.