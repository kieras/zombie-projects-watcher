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


def send_messages_to_chat(projects_by_owner):
    if not CHAT_ACTIVATED:
        logger.info('Chat integration is not active.')
        return

    for owner in projects_by_owner.keys():
        user_to_mention = USERS_MAP.get(owner, owner)
        message = "Hey *@{}*, I've noticed you are one of the owners of the following projects:\n\n".format(user_to_mention)
        for project in projects_by_owner.get(owner):
            project_id = project.get('projectId')
            org = ORGS_NAME_MAPPING.get(project.get('parent').get('id'))
            created_days_ago = int(project.get('createdDaysAgo'))
            cost = project.get('costSincePreviousMonth', 0.0)
            currency = project.get('costCurrency', '$')
            emoji = ''
            emoji_codepoint = chr(int(COST_ALERT_EMOJI, base = 16))
            cost_alert_emoji = "{} ".format(emoji_codepoint)
            if cost <= COST_MIN_TO_NOTIFY:
                logger.debug('- `{}/{}`, will not be in the message, due to its cost being lower than the minimum warning value'\
                    .format(owner, project_id))
            else:
                if cost > COST_ALERT_THRESHOLD:
                    emoji = ' ' + cost_alert_emoji
                send_message_to_this_owner = True
                message += "`{}/{}` created `{} days ago`, costing *`{}`* {}.{}\n"\
                    .format(org, project_id, created_days_ago, cost, currency, emoji)
                number_of_notified_projects = number_of_notified_projects + 1
        message += "\nIf these projects are not being used anymore, please consider `deleting them to reduce infra costs` and clutter."

        if send_message_to_this_owner:
            send_message(message)

    today_weekday=dt.today().strftime('%A')
    final_of_execution_message = f'Happy {today_weekday}! \
\nToday I found *{number_of_notified_projects} projects* with costs higher than the defined notification threshold of ${COST_MIN_TO_NOTIFY}.\
\n\n_Note: Only projects whose owner is a real user (and not a Service Account) were considered._'    
    send_message(final_of_execution_message)
