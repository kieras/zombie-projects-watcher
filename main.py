import logging
import logging.config
import json
from pprint import pformat
from datetime import datetime as dt
from googleapiclient import discovery

from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

from config import CONFIG
from utils import (
    extract_username,
    group_projects_by_owner
)
from filters import (
    filter_projects_matching_org_level,
    filter_older_than,
    filter_owners,
    filter_users,
    filter_whitelisted_projects,
    filter_whitelisted_users
)
from billing import query_billing_info
from slack import send_messages
from chat import send_messages_to_chat


ORGS_FILTER = CONFIG['filters']['orgs'].get()
PROJECTS_FILTER = CONFIG['filters']['projects'].get() or []
USERS_REGEX_FILTER = CONFIG['filters']['users_regex'].get() or []
AGE_MINIMUM_DAYS_FILTER = CONFIG['filters']['age_minimum_days'].get(int)
SLACK_ACTIVATED = CONFIG['slack']['activate'].get(bool)
CHAT_ACTIVATED = CONFIG['chat']['activate'].get(bool)
BILLING_ACTIVATED = CONFIG['billing']['activate'].get(bool)
DUMP_JSON_FILE_NAME = CONFIG['dump_json_file_name'].get()

DEBUG_ENRICHED_PROJECTS = CONFIG['debug']['enriched_projects'].get(bool)
DEBUG_FILTERED_BY_PROJECTS = CONFIG['debug']['filtered_by_projects'].get(bool)
DEBUG_FILTERED_BY_USERS = CONFIG['debug']['filtered_by_users'].get(bool)
DEBUG_FILTERED_BY_AGE = CONFIG['debug']['filtered_by_age'].get(bool)
DEBUG_GROUPED_BY_OWNERS = CONFIG['debug']['grouped_by_owners'].get(bool)
DEBUG_FILTERED_BY_ORGS = CONFIG['debug']['filtered_by_org'].get(bool)

def main():
    client = _get_resource_manager_client()

    logger.info('Retrieving Projects.')
    active_projects = _get_projects(client)

    logger.info('Calculating Project age information.')
    enriched_projects = _enrich_project_info_with_age(active_projects)

    logger.info('Retrieving Project owners information.')
    enriched_projects = _enrich_project_info_with_owners(client, enriched_projects)

    logger.info('Retrieving Project organization information.')
    enriched_projects = _enrich_project_info_with_orgs(client, enriched_projects)

    if BILLING_ACTIVATED:
        logger.info('Retrieving Project cost information.')
        enriched_projects = _enrich_project_info_with_costs(enriched_projects)
    else:
        logger.info('Project cost information is not active.')

    if DEBUG_ENRICHED_PROJECTS:
        logger.debug('Projects with enriched information:\n%s', pformat(enriched_projects))

    if DUMP_JSON_FILE_NAME:
        logger.debug('Dumping info to JSON file %s.', DUMP_JSON_FILE_NAME)
        with open(DUMP_JSON_FILE_NAME, 'w') as fp:
            json.dump(enriched_projects, fp, indent=2, sort_keys=True)

    logger.info('Filtering Projects by project.')
    project_filtered = list(filter(filter_whitelisted_projects(
        PROJECTS_FILTER), enriched_projects))

    if DEBUG_FILTERED_BY_PROJECTS:
        logger.debug('Project filter applied:\n%s', pformat(project_filtered))

    logger.info('Filtering Projects by user.')
    user_filtered = list(filter(filter_whitelisted_users(
        USERS_REGEX_FILTER), project_filtered))

    if DEBUG_FILTERED_BY_USERS:
        logger.debug('User filter applied:\n%s', pformat(user_filtered))

    logger.info('Filtering Projects by age.')
    older_projects = list(filter(filter_older_than(
        AGE_MINIMUM_DAYS_FILTER), user_filtered))

    if DEBUG_FILTERED_BY_AGE:
        logger.debug('Aged Projects filter applied:\n%s', pformat(older_projects))

    logger.info('Filtering Projects by org level.')
    
    org_projects = list(filter(filter_projects_matching_org_level(
        ORGS_FILTER), older_projects))

    if DEBUG_FILTERED_BY_ORGS:
        logger.debug('Project by orgs:\n%s', pformat(org_projects))

    logger.info('Grouping Projects by owner(s).')
    projects_by_owner = group_projects_by_owner(org_projects)

    if DEBUG_GROUPED_BY_OWNERS:
        logger.debug('Project by owner:\n%s', pformat(projects_by_owner))

    if SLACK_ACTIVATED:
        logger.info('Sending Slack messages.')
        send_messages(projects_by_owner)
        logger.info('All messages sent.')
    else:
        logger.info('Slack integration is not active.')

    if CHAT_ACTIVATED:
        logger.info('Sending Chat messages.')
        send_messages_to_chat(projects_by_owner)
        logger.info('All messages sent.')
    else:
        logger.info('Chat integration is not active.')

    logger.info('Happy Friday! :)')


def _get_projects(client):
    project_list_request = client.projects().search(query='state:ACTIVE')
    project_list_response = project_list_request.execute()
    projects = project_list_response.get('projects', [])
    while project_list_response.get('nextPageToken'):
        project_list_request = client.projects().list_next(previous_request=project_list_request,\
            previous_response=project_list_response)
        project_list_response = project_list_request.execute()
        projects = projects + project_list_response.get('projects', [])
    return projects


def _get_resource_manager_client():
    client = discovery.build("cloudresourcemanager", "v3")
    return client


def _enrich_project_info_with_owners(client, projects):
    for project in projects:
        project['owners'] = _get_owners(client, project)
        project['owners_id'] = _get_owners_id(project.get('owners'))
        logger.debug('Owners for Project %s: %s', project.get('projectId'), project.get('owners'))
    return projects


def _enrich_project_info_with_age(projects):
    for project in projects:
        project['createdDaysAgo'] = _get_created_days_ago(project)
    return projects


def _enrich_project_info_with_costs(projects):
    costs_by_project = query_billing_info()
    for project in projects:
        project['costSincePreviousMonthFull'] =\
            _get_cost_since_previous_month_full(costs_by_project, project)
        project['costSincePreviousMonth'] =\
            _get_cost_since_previous_month_value(costs_by_project, project)
        project['costCurrency'] =\
            _get_cost_currency(costs_by_project, project)
        project['costBillingAccountName'] =\
            _get_cost_billing_account_name(costs_by_project, project)
        project['costBillingAccountId'] =\
            _get_cost_billing_account_id(costs_by_project, project)
        logger.debug('Cost for Project %s: %s %s (Billing account: %s, Id: %s)',
            project.get('projectId'), project.get('costSincePreviousMonth'),
            project.get('costCurrency'), project.get('costBillingAccountName'),
            project.get('costBillingAccountId'))
    return projects


def _enrich_project_info_with_orgs(client, projects):
    for project in projects:
        project['org']=_get_organization(client, project)
        logger.debug('Organization root for Project %s: %s',project.get('projectId'), project.get('org'))
    return projects
    
    
    
def _get_cost_since_previous_month_full(costs_by_project, project):
    project_id = project.get('projectId')
    cost = costs_by_project.get(project_id, {})
    return cost


def _get_cost_since_previous_month_value(costs_by_project, project):
    cost = _get_cost_since_previous_month_full(costs_by_project, project)
    if not cost:
        return 0.0
    else:
        return cost.get('costGenerated', 0.0)


def _get_cost_currency(costs_by_project, project):
    cost = _get_cost_since_previous_month_full(costs_by_project, project)
    if not cost:
        return '$'
    else:
        return cost.get('currency', '$')


def _get_cost_billing_account_name(costs_by_project, project):
    cost = _get_cost_since_previous_month_full(costs_by_project, project)
    if not cost:
        return 'Unknown'
    else:
        return cost.get('billingAccountName', 'Unknown')


def _get_cost_billing_account_id(costs_by_project, project):
    cost = _get_cost_since_previous_month_full(costs_by_project, project)
    if not cost:
        return 'Unknown'
    else:
        return cost.get('billingAccountId', 'Unknown')


def _get_owners_id(owners):
    usernames = set([extract_username(user) for user in owners])
    return list(usernames)


def _get_owners(client, project):
    users = []
    project_name = project.get('name')
    iamPolicy = client.projects().getIamPolicy(resource=project_name, body={}).execute()
    bindings = iamPolicy.get('bindings', [])
    owners = list(filter(filter_owners, bindings))
    if not owners:
        logger.debug('No owners found for Project %s.', project_name)
    else:
        members = owners[0].get('members')
        users = list(filter(filter_users, members))
        if not users:
            logger.debug('No owner is a user for Project %s.', project_name)
    users = set([user.strip('user:') for user in users])
    return list(users)


def _get_organization(client, project):
    client = discovery.build("cloudresourcemanager", "v1")
    projectId = project.get('projectId')
    ancestry_request = client.projects().getAncestry(projectId=projectId, body=None)
    ancestry_response=ancestry_request.execute()
    for resourceId in ancestry_response['ancestor']:
        if resourceId['resourceId']['type'] == 'organization':
            org = resourceId['resourceId']['id']
    return org


def _get_created_days_ago(project):
    now = dt.now()
    create_time = project.get('createTime')
    create_date_value = dt.strptime(create_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    delta = now - create_date_value
    return delta.days


if __name__ == '__main__':
    main()
