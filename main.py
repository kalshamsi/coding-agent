import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
import json

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
    description = 'List files in the specified directory along with their sizes, constrained to the working directory. Call this first to see what files are available.',
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. Leave empty or use '.' to list files in the working directory itself.",
            ),
        },
        required=[],  # directory is optional
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

When a user asks a question or makes a request, you should use the available functions to gather information and complete tasks. You can perform the following operations:

- List files and directories (use get_files_info first to see what files are available)
- Read file contents (only after you know the file exists)
- Execute Python files with optional arguments
- Write or overwrite files

Give a response that has what you're thinking.

Always start by listing files with get_files_info to see what's available before trying to read specific files. If a file doesn't exist, don't keep trying to read it.

Always try to understand the complete file structure and directory contents before performing operations.

If you have gotten a file's contents before, you do NOT need to check it again, stop when you have the content you need.

IMPORTANT: When you have gathered enough information to answer the user's question completely, provide your final response starting with "Final response:" followed by your detailed answer.

IMPORTANT: DO NOT start any text without "Final response:" if it is not the final response.

Your final response should be comprehensive and address the user's question or request fully. Provide all relevant details and context. Be thorough and include steps if the process or inequiry relates to a process within the codebase.

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

def make_message(user_prompt):
    return types.Content(role="user", parts=[types.Part(text=user_prompt)])

def get_response(messages):
    return client.models.generate_content(
        config=types.GenerateContentConfig(
            tools=[available_functions],
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(
                    mode="AUTO",
                )
            ),
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
    
    for iteration in range(10):
        try:
            response = get_response(messages)
            candidate = response.candidates[0]
            
            # Check if there's any text in any part
            has_final_response = False
            for part in candidate.content.parts:
                if part.text and "Final response:" in part.text:
                    part.text = part.text.replace("Final response:", "").strip()
                    print("Final response:")
                    print(part.text)
                    has_final_response = True
                    break

            if has_final_response:
                break
            
            # Check if there are function calls
            function_calls = []
            for part in candidate.content.parts:
                if part.function_call:
                    function_calls.append(part.function_call)
            
            if function_calls:
                # Add the model's function call request to the conversation history
                messages.append(candidate.content)
                
                # Execute all function calls and collect responses
                tool_responses = []
                for func_call in function_calls:
                    tool_msg = call_function(func_call, verbose=verbose)
                    tool_responses.extend(tool_msg.parts)
                
                # Create a single tool response message with all function responses
                combined_tool_response = types.Content(
                    role="tool",
                    parts=tool_responses
                )
                messages.append(combined_tool_response)
            
            # Handle any non-final text responses
            elif any(part.text for part in candidate.content.parts):
                messages.append(candidate.content)
            
        except Exception as e:
            print(f"Error occurred: {e}")
            break


if __name__ == "__main__":
    main()