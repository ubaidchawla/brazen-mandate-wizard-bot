import os
import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from anthropic import Anthropic
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Load environment variables from .env file
load_dotenv()

# Initialize Anthropic client
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=anthropic_api_key)

# Initialize Slack client
slack_token = os.getenv("SLACK_API_TOKEN")
slack_client = WebClient(token=slack_token)

def get_google_sheet_data(spreadsheet_id, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds_file = os.getenv("GOOGLE_SHEET_CREDENTIALS")
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    data = sheet.get_all_records()
    return data

def post_message_to_slack(channel_id, text):
    try:
        slack_client.chat_postMessage(
            channel=channel_id,
            text=text
        )
        print("Message chunk posted to Slack successfully.")
    except SlackApiError as e:
        print(f"Error posting message chunk to Slack: {e.response['error']}")

def main():
    # Configuration from environment variables
    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    sheet_name = os.getenv("SHEET_NAME")
    prompt_spreadsheet_id = os.getenv("PROMPT_SPREADSHEET_ID")
    prompt_sheet_name = os.getenv("PROMPT_SHEET_NAME")
    slack_channel = os.getenv("SLACK_CHANNEL_ID")

    # Fetch data
    sheet_data = get_google_sheet_data(spreadsheet_id, sheet_name)
    prompt_sheet_data = get_google_sheet_data(prompt_spreadsheet_id, prompt_sheet_name)

    if prompt_sheet_data:
        # Convert sheet_data to a string (you may want to format this better)
        sheet_data_str = str(sheet_data)

        # Create a prompt message
        message = client.messages.create(
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

        # Extract the message content from the response
        response_text = message.content[0].text

        # Split the response into chunks of 3000 characters or less
        chunks = [response_text[i:i+3000] for i in range(0, len(response_text), 3000)]

        # Send each chunk to Slack
        for chunk in chunks:
            post_message_to_slack(slack_channel, chunk)
    else:
        print("Failed to fetch data from Google Sheets.")

if __name__ == "__main__":
    main()
