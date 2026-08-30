CREATE OR REPLACE TABLE main.governance_marketing.users_dq AS (
    WITH base AS (
        SELECT
        *,

        -- COMPLETENESS
        CASE WHEN user_id IS NULL THEN true ELSE false END AS dq_user_id_null,
        CASE WHEN email IS NULL THEN true ELSE false END AS dq_email_null,
        CASE WHEN signup_date IS NULL THEN true ELSE false END AS dq_signup_date_null,

        -- VALIDITY
        CASE 
            WHEN country IS NULL THEN true
            WHEN UPPER(country) NOT IN ('BR', 'US', 'UNKNOWN') THEN true 
            ELSE false 
        END AS dq_invalid_country,

        -- UNIQUENESS (check duplicates)
        CASE 
            WHEN COUNT(*) OVER (PARTITION BY user_id) > 1 THEN true
            ELSE false
        END AS dq_duplicate_user_id

    FROM main.silver_marketing.users 
    ),

    scored AS (
        SELECT 
            *,
            (
            CAST(dq_user_id_null AS INT) +
            CAST(dq_email_null AS INT) +
            CAST(dq_signup_date_null AS INT) +
            CAST(dq_invalid_country AS INT) +
            CAST(dq_duplicate_user_id AS INT)) AS dq_error_count
        FROM base

    )

    SELECT 
        *,
        CASE    
            WHEN dq_error_count = 0 THEN 'VALID' 
            ELSE 'INVALID'
        END AS dq_status,
        CURRENT_TIMESTAMP() AS dq_execution_timestamp
    FROM 
        scored
)

    