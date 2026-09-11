SELECT
    `case:concept:name` AS case_id,
    `concept:name` AS activity,
    `time:timestamp` AS event_timestamp,
    `org:group` AS department,
    Age AS age,
    Diagnose AS diagnosis,
    InfectionSuspected AS infection_suspected,
    Leucocytes AS leucocytes,
    CRP AS crp,
    LacticAcid AS lactic_acid

FROM `careflow-analytics-506719.careflow_raw.patient_events_clean`