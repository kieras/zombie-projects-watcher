import os
import json
import logging
import requests
from pprint import pformat
from config import CONFIG

logger = logging.getLogger(__name__)


ORGS_NAME_MAPPING = CONFIG['org_names_mapping'].get()
CHAT_ACTIVATED = CONFIG['chat']['activate'].get(bool)
WEBHOOK_URL = CONFIG['chat']['webhook_url'].get()
USERS_MAP = CONFIG['chat']['users_mapping'].get()
PRINT_ONLY = CONFIG['chat']['print_only'].get(bool)
COST_ALERT_THRESHOLD = CONFIG['chat']['cost_alert_threshold'].get(float)
COST_ALERT_EMOJI = CONFIG['chat']['cost_alert_emoji'].get()
COST_MIN_TO_NOTIFY = CONFIG['chat']['cost_min_to_notify'].get(float)


def send_messages_to_chat(projects_by_owner):
    if not CHAT_ACTIVATED:
        logger.info('Chat integration is not active.')
        return

    for owner in projects_by_owner.keys():
        user_to_mention = USERS_MAP.get(owner, owner)
        message = "Hey *@{}*, I've noticed you are one of the owners of the following projects:\n\n".format(user_to_mention)
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
        message += "\nIf these projects are not being used anymore, please consider `deleting them to reduce infra costs` and clutter. :rip:"

        if send_message_to_this_owner:
            logger.info('Sending Chat message to webhook %s:\n%s', WEBHOOK_URL, message)
            if PRINT_ONLY:
                return
            message_headers = {'Content-Type': 'application/json; charset=UTF-8'}
            message_data = {
                'text': message
            }
            message_data_json = json.dumps(message_data, indent=2)
            response = requests.post(
                WEBHOOK_URL, data=message_data_json, headers=message_headers)
            if response.status_code != 200:
                logger.error('Error sending message to Chat. Error: %s, Response: %s, Webhook: %s', response.status_code, pformat(response.text), WEBHOOK_URL)
