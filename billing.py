import logging
from config import CONFIG
from google.cloud import bigquery

logger = logging.getLogger(__name__)

BIGQUERY_CLIENT_PROJECT = CONFIG['billing']['bigquery_client_project'].get()
COST_VIEW_FULL_NAME = CONFIG['billing']['cost_view_full_name'].get()

def query_billing_info():
    client = bigquery.Client(project=BIGQUERY_CLIENT_PROJECT)
    query_job = client.query("""
        SELECT
            billing_account_name
        ,   billing_account_id
        ,   project_id
        ,   cost_generated
        ,   currency
        ,   cost_reference_start_date
        FROM
            `{}`
        ORDER BY
            cost_generated DESC
        LIMIT 1000
    """.format(COST_VIEW_FULL_NAME))
    
    logger.debug('Executing cost query.')
    results = query_job.result()
    
    results_by_project = {}
    for row in results:
        results_by_project[row.project_id] = {
            'billingAccountName': row.billing_account_name,
            'billingAccountId': row.billing_account_id,
            'projectId': row.project_id,
            'costGenerated': row.cost_generated,
            'currency': row.currency,
            'costReferenceStartDate': row.cost_reference_start_date.strftime('%Y-%m-%d')
        }

    return results_by_project
