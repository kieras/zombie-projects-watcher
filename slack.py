from curses import init_pair
import os
import logging
from pprint import pformat
from slackclient import SlackClient
from config import CONFIG
from datetime import datetime as dt

logger = logging.getLogger(__name__)

slack_token = os.getenv("SLACK_API_TOKEN")
sc = SlackClient(slack_token)

ORGS_NAME_MAPPING = CONFIG['org_names_mapping'].get()
SLACK_ACTIVATED = CONFIG['slack']['activate'].get(bool)
USERS_MAP = CONFIG['slack']['users_mapping'].get()
PRINT_ONLY = CONFIG['slack']['print_only'].get(bool)
TEST_USER = CONFIG['slack']['test_user'].get()
TEAM_CHANNEL = CONFIG['slack']['team_channel'].get()
SEND_TO_TEAM_CHANNEL = CONFIG['slack']['send_to_team_channel'].get(bool)
TEAM_CHANNEL_FALLBACK = CONFIG['slack']['team_channel_fallback'].get(bool)
BOT_NAME = CONFIG['slack']['bot']['name'].get()
BOT_EMOJI = CONFIG['slack']['bot']['emoji'].get()
COST_ALERT_THRESHOLD = CONFIG['slack']['cost_alert_threshold'].get(float)
COST_ALERT_EMOJI = CONFIG['slack']['cost_alert_emoji'].get()
COST_MIN_TO_NOTIFY = CONFIG['slack']['cost_min_to_notify'].get(float)


def prepare_message(slack_user, message):
    slack_channel = "@{}".format(slack_user)
    if SEND_TO_TEAM_CHANNEL:
        slack_channel = "#{}".format(TEAM_CHANNEL)
    resp = _send_message(slack_channel, message)
    if resp and not resp.get('ok'):
        if resp.get('error') == 'channel_not_found':
            logger.error('Error: %s, Channel: %s', resp.get('error'), slack_channel)
            if TEAM_CHANNEL_FALLBACK:
                resp = _send_message("#{}".format(TEAM_CHANNEL), message)
                if resp and not resp.get('ok'):
                    logger.error('Error in fallback to team channel: %s, Channel: %s, Response: %s', resp.get('error'), slack_channel, pformat(resp))
            else:
                logger.error('Error: %s, Channel: %s, Response: %s', resp.get('error'), slack_channel, pformat(resp))

def send_messages_to_slack(projects_by_owner):
    number_of_notified_projects = 0
    if not SLACK_ACTIVATED:
        logger.info('Slack integration is not active.')
        return

    today_weekday=dt.today().strftime('%A')
    initial_message = f'Happy {today_weekday}!'
    prepare_message(TEAM_CHANNEL, initial_message)

    for owner in projects_by_owner.keys():
        slack_user = USERS_MAP.get(owner, owner)
        message = "Hey @{}, I've noticed you are one of the owners of the following projects:\n".format(slack_user)
        send_message_to_this_owner = False
        for project in projects_by_owner.get(owner):
            project_id = project.get('projectId')
            org = ORGS_NAME_MAPPING.get(project.get('org'))
            created_days_ago = int(project.get('createdDaysAgo'))
            cost = project.get('costSincePreviousMonth', 0.0)
            currency = project.get('costCurrency', '$')
            emoji = ''
            if cost <= COST_MIN_TO_NOTIFY:
                logger.debug('- `{}/{}`, will not be in the message, due to its cost being lower than the minimum warning value'.format(owner, project_id))
            else:
                if cost > COST_ALERT_THRESHOLD:
                    emoji = ' ' + COST_ALERT_EMOJI
                send_message_to_this_owner = True
                message += "- `{}/{}` created `{} days ago`, costing *`{}`* {}.{}\n".format(org, project_id, created_days_ago, cost, currency, emoji)
                number_of_notified_projects = number_of_notified_projects + 1       
        message += "If these projects are not being used anymore, please consider `deleting them to reduce infra costs` and clutter. :rip:"
        
        if send_message_to_this_owner:
            prepare_message(slack_user, message)

    final_of_execution_message = '\nToday I found *{number_of_notified_projects} projects* with costs higher \
        than the defined notification threshold ${COST_MIN_TO_NOTIFY}.\
        \n\n_Note: Only projects whose owner is a real user (and not a Service Account) were considered._'           

    prepare_message(TEAM_CHANNEL, final_of_execution_message)

def _send_message(channel, message):
    if TEST_USER:
        channel = "@{}".format(TEST_USER)

    logger.info('Sending Slack message to channel %s:\n%s', channel, message)

    if PRINT_ONLY:
        return

    resp = sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=message,
        as_user="false",
        username=BOT_NAME,
        icon_emoji=BOT_EMOJI,
        link_names="true"
    )
    return resp
