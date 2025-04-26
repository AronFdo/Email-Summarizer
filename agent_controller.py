import os
from dotenv import load_dotenv
from agents_mcp import Agent
from openai import OpenAI

load_dotenv()  # load variables from .env

class EmailSummarizerAgent(Agent):
    def __init__(self, model_name="gpt-4-turbo"):
        super().__init__(name="EmailSummarizerAgent")
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = model_name

    def summarize_email(self, email_text):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Summarize this email in 1-2 sentences:\n\n{email_text}"}
            ]
        )
        return response.choices[0].message.content

    def suggest_action(self, email_text):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Given this email:\n\n{email_text}\n\nSuggest an action (Reply, Archive, Schedule, Ignore):"}
            ]
        )
        return response.choices[0].message.content
    
    def generate_reply(self, email_text):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Given this email:\n\n{email_text}\n\nWrite a professional and polite reply. Keep it concise."}
            ]
        )
        return response.choices[0].message.content