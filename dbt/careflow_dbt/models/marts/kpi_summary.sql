SELECT
    COUNT(*) AS total_patients,

    COUNTIF(admission_time IS NOT NULL) AS total_admissions,

    COUNTIF(release_time IS NOT NULL) AS total_releases,

    COUNTIF(er_return_count > 0) AS patients_with_er_return,

    ROUND(
        AVG(er_to_admission_minutes),
        2
    ) AS average_er_to_admission_minutes,

    ROUND(
        AVG(admission_to_release_hours),
        2
    ) AS average_hospital_stay_hours,

    SUM(total_events) AS total_events

FROM {{ ref('patient_journey_summary') }}