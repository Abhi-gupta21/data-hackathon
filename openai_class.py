import openai
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

class my_openai:
    def __init__(self, prompt):
        self.prompt = prompt

    def generate_text(self):

        client = OpenAI()
        openai.api_key=os.getenv('API_KEY')
        completion = client.chat.completions.create(
          model="gpt-3.5-turbo",
          messages=[
            {"role": "system", "content": "You are an assistant, skilled in creating linkedin posts based on a prompt."},
            {"role": "user", "content": self.prompt}
          ]
        )
        return completion.choices[0].message.content




