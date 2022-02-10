# Zombie Projects Watcher

Helps your team control infra costs by pointing potential unused 'zombie' projects.

Owners of the Projects receive messages like this one:

![Example Slack message](example-slack-message.png?raw=true "Example Slack message")

Messages like this one are sent to your Chat room:

![Example Chat message](example-chat-message.png?raw=true "Example Chat message")

## Installation

### Dependencies and Config

Clone this repository.

Install Python dependencies and prepare the config file:

```bash
pipenv install --ignore-pipfile --dev
cp example-config.yaml config.yaml
```

Change `config.yaml` to you needs

### Usage as a CLI command


You can execute the program with your user authenticated in the using gcloud:

```bash
gcloud auth application-default login
gcloud config set project PROJECT_ID
```

If you want, you can use a Service Account to authenticate by exporting the following variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS='service-account-key.json'
```

Run the following command:

```bash
pipenv run python main.py
```

If you have created an API token for the Slack integration, execute the following commands:

```bash
export SLACK_API_TOKEN=<your Slack API token>
pipenv run python main.py
```

See the `example-bigquery-billing-costs-view.sql` file of an example query to use for adding Project cost information from your [Billing Export](https://cloud.google.com/billing/docs/how-to/export-data-bigquery) data in BigQuery.

### Usage as a Google Cloud Function

If you want to deploy the code as a Cloud Function, run the following command:

```bash
gcloud functions deploy zombie-project-watcher \
--entry-point=http_request \
--runtime python38 \
--trigger-http
```

If you need to run or debug the  Google Cloud Function locally, run the command:

```bash
functions-framework --target http_request --debug
```
