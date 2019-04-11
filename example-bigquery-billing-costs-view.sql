SELECT
    '<billing_account_name1>' AS billing_account_name
,   billing_account_id
,   project.id AS project_id
,   ROUND(SUM(cost), 2) AS cost_generated
,   currency
,   DATE_SUB(DATE_TRUNC(current_date, MONTH), INTERVAL 1 MONTH) AS cost_reference_start_date
FROM
    `<project1>.<billing_dataset1>.<gcp_billing_export_table1>`
WHERE
    project.id IS NOT NULL
    -- the cost occurred after cost_reference_start_date (first day of previous month)
    AND PARSE_DATE("%Y-%m-%d", FORMAT_TIMESTAMP("%Y-%m-%d", usage_start_time)) 
          >= DATE_SUB(DATE_TRUNC(current_date, MONTH), INTERVAL 1 MONTH)
GROUP BY
    billing_account_name
,   billing_account_id
,   project.id
,   currency
,   cost_reference_start_date
UNION ALL
SELECT
    '<billing_account_name2>' AS billing_account_name
,   billing_account_id
,   project.id AS project_id
,   ROUND(SUM(cost), 2) AS cost_generated
,   currency
,   DATE_SUB(DATE_TRUNC(current_date, MONTH), INTERVAL 1 MONTH) AS cost_reference_start_date
FROM
    `<project2>.<billing_dataset2>.<gcp_billing_export_table2>`
WHERE
    project.id IS NOT NULL
    -- the cost occurred after cost_reference_start_date (first day of previous month)
    AND PARSE_DATE("%Y-%m-%d", FORMAT_TIMESTAMP("%Y-%m-%d", usage_start_time)) 
          >= DATE_SUB(DATE_TRUNC(current_date, MONTH), INTERVAL 1 MONTH)
GROUP BY
    billing_account_name
,   billing_account_id
,   project.id
,   currency
,   cost_reference_start_date
