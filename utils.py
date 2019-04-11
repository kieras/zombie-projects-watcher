import re
from config import CONFIG

ORGS_NAME_MAPPING = CONFIG['org_names_mapping'].get()

def group_projects_by_owner(projects):
    projects_by_owner = {}
    for project in projects:
        owners = project.get('owners_id')
        for owner in owners:
            prjs = projects_by_owner.setdefault(owner, [])
            prjs.append(project)
    return projects_by_owner


def extract_username(member):
    username = re.search('(.*)@.*', member).group(1)
    return username


def print_info(projects):
    print('#{} projects.'.format(len(projects)))
    for project in projects:
        project_id = project.get('projectId')
        org = ORGS_NAME_MAPPING.get(project.get('parent').get('id'))
        created_days_ago = int(project.get('createdDaysAgo', '-1'))
        cost_value = project.get('costSincePreviousMonth', 'Unknown')
        cost_currency = project.get('costCurrency', 'Unknown')
        owners = project.get('owners', 'Unknown')
        owners_id = project.get('owners_id', 'Unknown')
        created_time = project.get('createTime', 'Unknown')
        print('{}/{}, CreatedTime={}, Age={}d, Cost={} {}, Owners={}, '
            'Users={}.'.format(
            org, project_id, created_time, created_days_ago, cost_value,
            cost_currency, owners, owners_id))
