# main.py

from email_client import GmailClient
from agent_controller import EmailSummarizerAgent
import re

def extract_email(sender_string):
    """Extract email address from a sender string."""
    # Try to find an email pattern like <email@example.com>
    email_match = re.search(r'<([^<>]+@[^<>]+)>', sender_string)
    if email_match:
        return email_match.group(1)
    
    # If no <> format, try to find a raw email
    email_match = re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', sender_string)
    if email_match:
        return email_match.group(1)
    
    # Return original if no match (will likely cause an error, but better for debugging)
    return sender_string

def main():
    # Step 1: Initialize Gmail client
    gmail_client = GmailClient()
    latest_emails = gmail_client.get_latest_emails()

    # Step 2: Initialize the AI agent
    agent = EmailSummarizerAgent()

    # Step 3: Process each email
    for idx, email in enumerate(latest_emails, 1):
        print("=" * 50)
        print(f"📩 Email {idx}")
        print(f"From: {email['sender']}")
        print(f"Subject: {email['subject']}")

        # Summarize the email
        summary = agent.summarize_email(email['body'])
        print(f"📝 Summary: {summary}")

        # Suggest an action
        action = agent.suggest_action(email['body'])
        print(f"✅ Suggested Action: {action}")

        # If the suggested action is "Reply", generate a reply and create a draft
        if "reply" in action.lower():
            reply_text = agent.generate_reply(email['body'])
            print(f"✍️ Generated Reply: {reply_text}")

            # Extract clean email address from sender
            to_address = extract_email(email['sender'])
            subject = f"Re: {email['subject']}"
            
            # Print for debugging
            print(f"Sending to: {to_address}")
            
            try:
                gmail_client.create_draft(to_address, subject, reply_text)
                print(f"💾 Draft created for {to_address}")
            except Exception as e:
                print(f"Error creating draft: {str(e)}")
                print(f"Using sender: {email['sender']}")
                print(f"Extracted email: {to_address}")

        print("=" * 50 + "\n")

if __name__ == "__main__":
    main()