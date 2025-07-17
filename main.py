import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python_file import run_python_file
from functions.call_functions import call_function

verbose = False

def ingest_user_input():
    global verbose
    user_prompt = ""
    if len(sys.argv) < 2:
        print("Usage: uv run main.py <content> [--verbose]")
        sys.exit(1)
    
    if len(sys.argv) > 2:
        if sys.argv[2] == '--verbose':
            verbose = True
    
    user_prompt = sys.argv[1]
    return user_prompt

def setup():
    load_dotenv()
    return os.environ.get("GEMINI_API_KEY")


# Define the schema for the get_files_info function
schema_get_files_info = types.FunctionDeclaration(
    name = 'get_files_info',
    description = 'List files in the specified directory along with their sizes, constrained to the working directory.',
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provied, lists files in the working directory itself.",
            ),
        },
    ),
)

# Define the schema for the get_file_content function
schema_get_file_content = types.FunctionDeclaration(
    name = 'get_file_content',
    description = 'Get the content of a file, constrained to the working directory.',
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file relative to the working directory.",
            ),
        },
    ),
)

# Define the schema for the run_python_file function
schema_run_python_file = types.FunctionDeclaration(
    name = 'run_python_file',
    description = 'Run a Python file, constrained to the working directory.',
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file relative to the working directory.",
            ),
        },
    ),
)

# Define the schema for the write_file function
schema_write_file = types.FunctionDeclaration(
    name = 'write_file',
    description = 'Write content to a file, constrained to the working directory.',
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            ),
        },
    ),
)

# Available functions
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

client = genai.Client(api_key = setup())

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

def make_message(user_prompt):
    return types.Content(role="user", parts=[types.Part(text=user_prompt)])

def get_response(messages):
    return client.models.generate_content(
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt
        ),
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

    # use call_function to handle any function calls in the response
    if response.candidates[0].content.parts[0].function_call:
        func_call = response.candidates[0].content.parts[0].function_call
        call_response = call_function(func_call, verbose=verbose)
        if verbose:
            print(f"-> {call_response.parts[0].function_response.response}")

    # Print the AI's response
    if response.candidates and len(response.candidates) > 0:
        candidate = response.candidates[0]
        if hasattr(candidate, 'content') and candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if hasattr(part, 'text') and part.text:
                    print(part.text)
        elif response.function_calls:
            # If there's no text response but there were function calls, that's normal
            pass
        else:
            print("No text response from AI.")
    else:
        print("No response candidates found.")

if __name__ == "__main__":
    response = main()