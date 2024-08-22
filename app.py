import os
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from anthropic import Anthropic
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from datetime import datetime, timedelta, date
from dateutil import parser

# Load environment variables from .env file
load_dotenv()

# Initialize Anthropic client
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
anthropic_client = Anthropic(api_key=anthropic_api_key)

# Initialize Slack Bolt App
slack_bot_token = os.getenv("SLACK_BOT_TOKEN")
slack_app_token = os.getenv("SLACK_APP_TOKEN")
app = App(token=slack_bot_token)

def get_prompt_sheet_data(spreadsheet_id, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds_file = os.getenv("GOOGLE_SHEET_CREDENTIALS")
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    data = sheet.get_all_records()
    return data

def get_google_sheet_data(spreadsheet_id, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds_file = os.getenv("GOOGLE_SHEET_CREDENTIALS")
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    data = sheet.get_all_records()

    # Filter data for the last 7 days
    today = date.today()
    seven_days_ago = today - timedelta(days=7)
    filtered_data = []

    for row in data:
        submitted_at = row.get('Submitted At')
        if submitted_at:
            try:
                # Parse the date from the string and ignore the time
                submitted_date = datetime.strptime(submitted_at.split()[0], '%d/%m/%Y').date()

                print(f"seven_days_ago: {seven_days_ago}")
                print(f"submitted_date: {submitted_date}")

                # Compare the parsed date with the seven_days_ago date
                if seven_days_ago <= submitted_date <= today:
                    print("YES!!")
                    filtered_data.append(row)
            except ValueError as e:
                print(f"Error parsing date: {submitted_at}. Error: {e}")
                continue

    print(f"filtered_data: {filtered_data}")
    return filtered_data

def generate_report():
    # Configuration from environment variables
    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    sheet_name = os.getenv("SHEET_NAME")
    prompt_spreadsheet_id = os.getenv("PROMPT_SPREADSHEET_ID")
    prompt_sheet_name = os.getenv("PROMPT_SHEET_NAME")

    # Fetch data
    sheet_data = get_google_sheet_data(spreadsheet_id, sheet_name)
    prompt_sheet_data = get_prompt_sheet_data(prompt_spreadsheet_id, prompt_sheet_name)

    if prompt_sheet_data:
        sheet_data_str = str(sheet_data)

        message = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            temperature=0,
            system=prompt_sheet_data[0]['system_prompts'],
            messages=[
                {
                    "role": "user",
                    "content": f"Please give a summary for this data: {sheet_data_str}"
                }
            ]
        )

        response_text = message.content[0].text
        return response_text
    else:
        return "Failed to fetch data from Google Sheets."

@app.event("app_mention")
def handle_mention(event, say, client):
    text = event["text"]
    if "report" in text.lower():
        # Send the initial "waiting" message and capture its timestamp
        result = say("Generating report... Please wait.")
        waiting_message_ts = result['ts']
        
        # Generate the report
        report = generate_report()
        
        try:
            # Delete the "waiting" message
            client.chat_delete(
                channel=event['channel'],
                ts=waiting_message_ts
            )
        except SlackApiError as e:
            print(f"Error deleting message: {e}")

        # Send the report in chunks
        chunks = [report[i:i+3000] for i in range(0, len(report), 3000)]
        for chunk in chunks:
            say(chunk)

if __name__ == "__main__":
    handler = SocketModeHandler(app, slack_app_token)
    handler.start()