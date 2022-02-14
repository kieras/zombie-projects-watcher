# Zombie Projects Watcher

Helps your team control infra costs by pointing potential unused 'zombie' projects.

If you use the Slack integration, the Owners of the Projects receive messages like this one:"

![Example Slack message](example-slack-message.png?raw=true "Example Slack message")

If you use the Google Chat integration, messages similar to this one are sent to your Chat Space:

![Example Chat message](example-chat-message.png?raw=true "Example Chat message")

## Installation

### Dependencies and Config

Clone this repository.

Install Python dependencies and prepare the config file:

```bash
pipenv install --ignore-pipfile --dev
cp example-config.yaml config.yaml
```

Change `config.yaml` to fit your needs.

### Usage as a CLI command


If you want to execute the program using your GCP user credentials, use the commands below:
```bash
gcloud auth application-default login
gcloud config set project PROJECT_ID
```

Instead of using your GCP user credentials, you can use a Service Account Key. In this case, use the following command:

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
