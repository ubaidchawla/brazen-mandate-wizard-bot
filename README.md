BRAZEN MANDATE WIZARD BOT

This project integrates Google Sheets with Slack and Anthropic's API to fetch data from Google Sheets, generate a summary using Anthropic, and post the summary to a Slack channel.

## Features

- Fetch data from Google Sheets
- Generate a summary using Anthropic's API
- Post the summary to Slack

## Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)
- A Google Cloud project with a service account for Google Sheets API access
- Slack API token
- Anthropic API key

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ubaidchawla/brazen-mandate-wizard-bot.git
   cd brazen-mandate-wizard-bot


2. **Set Up the Environment Variables:**
    ```env
    ANTHROPIC_API_KEY=your_anthropic_api_key
    SLACK_API_TOKEN=your_slack_api_token
    SPREADSHEET_ID=your_spreadsheet_id
    SHEET_NAME=your_sheet_name
    PROMPT_SPREADSHEET_ID=your_prompt_spreadsheet_id
    PROMPT_SHEET_NAME=your_prompt_sheet_name
    SLACK_CHANNEL_ID=your_slack_channel_id
    GOOGLE_SHEET_CREDENTIALS=service-account.json
    ```
3. **Google Sheets API Credentials**
Ensure you have the Google Sheets API credentials file in the project directory.

4. **Build and Run with Docker**
    1. Build the Docker Image
    ```bash
        docker build -t bmw-bot .
    ```
        
    2. Run the Docker Container
        ```bash
        docker run -d --env-file .env --name bmw-bot-container bmw-bot
        ```

