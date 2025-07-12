import os

def write_file(working_directory, file_path, content):
    path = os.path.join(working_directory, file_path)
    path = os.path.abspath(path)
    if not path.startswith(os.path.abspath(working_directory)):
        return (f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory')
    try:
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
    except Exception as e:
        return f'Error: {e}'
    
    try:
        with open(path, 'w') as file:
            file.write(content)
            return f"Successfully wrote to '{file_path}' {len(content)} characters written"
    except Exception as e:
        return f'Error: {e}'
    return None
