import os
import subprocess

def run_python_file(working_directory, file_path):
    path = os.path.join(working_directory, file_path)
    path = os.path.abspath(path)
    if not path.startswith(os.path.abspath(working_directory)):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(path):
        return f'Error: File "{file_path}" not found.'
    if not path.endswith('.py'):
        return f'Error: File "{file_path}" is not a Python file.'
    
    try:
        result = subprocess.run(['python', path], capture_output = True, timeout = 30, text = True)
        
        result_list = []

        if result.stdout:
            result_list.append(f"STDOUT: {result.stdout}")
        if result.stderr:
            result_list.append(f"STDERR: {result.stderr}")
        if result.returncode != 0:
            result_list.append(f"Process exited with code {result.returncode}")
    except Exception as e:
        return f'Error: executing Python file: {e}' 

    return "\n".join(result_list) if result_list else "No output produced."       
