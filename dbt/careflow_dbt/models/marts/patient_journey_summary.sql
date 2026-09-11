WITH patient_events AS (

    SELECT *
    FROM {{ ref('stg_patient_events') }}

),

patient_summary AS (

    SELECT
        case_id,

        MIN(event_timestamp) AS first_event_time,

        MIN(CASE
            WHEN activity = 'ER Registration'
            THEN event_timestamp
        END) AS er_registration_time,

        MIN(CASE
            WHEN activity = 'Admission NC'
            THEN event_timestamp
        END) AS admission_time,

        MAX(CASE
            WHEN activity LIKE 'Release%'
            THEN event_timestamp
        END) AS release_time,

        COUNT(*) AS total_events,

        COUNTIF(activity = 'Return ER') AS er_return_count,

        ANY_VALUE(age) AS age,

        ANY_VALUE(diagnosis) AS diagnosis,

        ANY_VALUE(infection_suspected) AS infection_suspected

    FROM patient_events

    GROUP BY case_id

)

SELECT
    *,
    
    TIMESTAMP_DIFF(
        admission_time,
        er_registration_time,
        MINUTE
    ) AS er_to_admission_minutes,

    TIMESTAMP_DIFF(
        release_time,
        admission_time,
        HOUR
    ) AS admission_to_release_hours

FROM patient_summary