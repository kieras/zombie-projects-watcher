import re


def filter_active_projects_matching_org_level(orgs):
    def filter_projects(project):
        if project.get('state') == 'ACTIVE': 
            return True
        else:
            return False
    return filter_projects


def filter_whitelisted_projects(whitelisted_project_ids):
    def filter_projects(project):
        if project.get('projectId') not in whitelisted_project_ids:
            return True
        else:
            return False
    return filter_projects


def filter_older_than(days):
    def filter_older_projects(project):
        if int(project.get('createdDaysAgo')) > days:
            return True
        else:
            return False
    return filter_older_projects


def filter_owners(bindings):
    if bindings.get('role') == 'roles/owner':
        return True
    else:
        return False


def filter_users(member):
    if 'user:' in member:
        return True
    else:
        return False


def filter_whitelisted_users(whitelisted_users_regex):
    def filter_users(project):
        for owner in project.get('owners'):
            for whitelisted_user in whitelisted_users_regex:
                if re.search(whitelisted_user, owner):
                    return False
        return True
    return filter_users
