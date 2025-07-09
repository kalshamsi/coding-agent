import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

verbose = False

def ingest_user_input():
    global verbose
    user_prompt = ""
    if len(sys.argv) < 2:
        print("Usage: python main.py <content> [--verbose]")
        sys.exit(1)
    
    if len(sys.argv) > 2:
        if sys.argv[2] == '--verbose':
            verbose = True
    
    user_prompt = sys.argv[1]
    return user_prompt

def setup():
    load_dotenv()
    return os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key = setup())

def make_message(user_prompt):
    return types.Content(role="user", parts=[types.Part(text=user_prompt)])

def get_response(messages):
    return client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages
    )

def main():
    user_prompt = ingest_user_input()
    if not user_prompt:
        print("No user prompt provided.")
        sys.exit(1)

    messages = [make_message(user_prompt)]
    response = get_response(messages)
    
    if verbose:
        print(f"User prompt: {user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}\nResponse tokens: {response.usage_metadata.candidates_token_count}")

if __name__ == "__main__":
    response = main()