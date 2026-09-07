{{ config(materialized="table") }}

select
    patient_id,
    any_value(visit_type) as visit_type,
    any_value(priority) as priority,
    min(event_time) as first_event_time,
    max(event_time) as discharge_time,
    timestamp_diff(max(event_time), min(event_time), minute) as journey_minutes,
    sum(wait_minutes) as total_wait_minutes,
    count(*) as event_count
from {{ ref("stg_patient_events") }}
group by patient_id