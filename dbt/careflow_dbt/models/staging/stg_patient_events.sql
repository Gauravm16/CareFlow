{{ config(materialized="table") }}

select
    patient_id,
    event_name,
    event_time,
    department,
    visit_type,
    priority,
    wait_minutes
from `careflow-analytics-506719.careflow_raw.patient_events`
where patient_id is not null