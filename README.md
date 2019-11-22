# Zombie Projects Watcher

Helps your team control infra costs by pointing potential unused 'zombie' projects.

## Installation

Clone this repository.

Install Python dependencies and prepare the config file:

```bash
pipenv install --ignore-pipfile --dev
cp example-config.yaml config.yaml
```

## Usage

Change `config.yaml` to you needs and run the following command:

```bash
pipenv run python main.py
```

If you have created an API token for the Slack integration, execute the following commands:

```bash
export SLACK_API_TOKEN=<your Slack API token>
pipenv run python main.py
```

See the `example-bigquery-billing-costs-view.sql` file of an example query to use for adding Project cost information from your [Billing Export](https://cloud.google.com/billing/docs/how-to/export-data-bigquery) data in BigQuery.

## Example message on Slack

Owners of the Projects receive messages like this one:

![Example Slack message](example-slack-message.png?raw=true "Example Slack message")

## Example message on Chat

Messages like this one are sent to your Chat room:

![Example Chat message](example-chat-message.png?raw=true "Example Chat message")
