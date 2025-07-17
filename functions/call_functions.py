import json
from google import genai
from google.genai import types
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file

function_map = {
            "get_files_info": get_files_info,
            "get_file_content": get_file_content,
            "run_python_file": run_python_file,
            "write_file": write_file
        }
        

def call_function(function_call_part, verbose=False):
    if function_call_part:
        func_name = function_call_part.name
        func_args = function_call_part.args
        func_args_dict = json.loads(func_args) if isinstance(func_args, str) else func_args

        if verbose:
            print(f"Calling function: {func_name}({func_args_dict})")
        else:
            print(f" - Calling function: {func_name}")

        # Dynamically call the function by name, but always specify the working directory ./calculator
        # use unpacking to pass the other arguments
        
        # Then use the mapping to call the function
        working_directory = "./calculator"
        if func_name in function_map:
            func_results = function_map[func_name](working_directory = working_directory, **func_args_dict)
        else:
            return types.Content(
                role = "tool",
                parts = [
                    types.Part.from_function_response(
                        name = func_name,
                        response = {"error": f"Unknown function: {func_name}"}
                    )
                ],
            )
    
        return types.Content(
            role = "tool",
            parts = [
                types.Part.from_function_response(
                    name = func_name,
                    response = {"result": func_results}
                )
            ]
        )