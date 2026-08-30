CREATE TABLE IF NOT EXISTS main.governance_marketing.users_dq_metrics (
    table_name STRING,
    execution_timestamp TIMESTAMP,
    total_records BIGINT,
    total_valid BIGINT,
    total_invalid BIGINT,
    quality_percentage DOUBLE,

    -- métricas por regra
    user_id_null_count BIGINT,
    email_null_count BIGINT,
    signup_date_null_count BIGINT,
    invalid_country_count BIGINT,
    duplicate_user_id_count BIGINT
);


INSERT INTO main.governance_marketing.users_dq_metrics
  SELECT
      'users' AS table_name,
      MAX(dq_execution_timestamp) AS execution_timestamp,
      
      COUNT(*) AS total_records,
      SUM(CASE WHEN dq_status = 'VALID' THEN 1 ELSE 0 END) AS total_valid,
      SUM(CASE WHEN dq_status = 'INVALID' THEN 1 ELSE 0 END) AS total_invalid,
      
      ROUND(
          100.0 * SUM(CASE WHEN dq_status = 'VALID' THEN 1 ELSE 0 END) / COUNT(*),
          2
      ) AS quality_percentage,

      SUM(CAST(dq_user_id_null AS INT)) AS user_id_null_count,
      SUM(CAST(dq_email_null AS INT)) AS email_null_count,
      SUM(CAST(dq_signup_date_null AS INT)) AS signup_date_null_count,
      SUM(CAST(dq_invalid_country AS INT)) AS invalid_country_count,
      SUM(CAST(dq_duplicate_user_id AS INT)) AS duplicate_user_id_count

  FROM main.governance_marketing.users_dq;


SELECT * FROM main.governance_marketing.users_dq_metrics
