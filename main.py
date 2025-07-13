import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python_file import run_python_file

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

    # Handle function calls if any
    if response.function_calls:
        for function_call in response.function_calls:
            print(f"Calling function: {function_call.name}({function_call.args})")
            
            # Get the working directory (current directory)
            working_directory = os.getcwd()
            
            # Execute the appropriate function
            if function_call.name == "get_files_info":
                directory = function_call.args.get("directory", "") if function_call.args else ""
                result = get_files_info(working_directory, directory)
            elif function_call.name == "get_file_content":
                file_path = function_call.args.get("file_path", "") if function_call.args else ""
                result = get_file_content(working_directory, file_path)
            elif function_call.name == "run_python_file":
                file_path = function_call.args.get("file_path", "") if function_call.args else ""
                result = run_python_file(working_directory, file_path)
            elif function_call.name == "write_file":
                file_path = function_call.args.get("file_path", "") if function_call.args else ""
                content = function_call.args.get("content", "") if function_call.args else ""
                result = write_file(working_directory, file_path, content)
            else:
                result = f"Unknown function: {function_call.name}"
            
            print(f"Function result: {result}")
    
    if verbose:
        print(f"User prompt: {user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}\nResponse tokens: {response.usage_metadata.candidates_token_count}")
    
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