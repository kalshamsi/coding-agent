import os
MAX_CHAR = 10_000


def get_file_content(working_directory, file_path):
    path = os.path.join(working_directory, file_path)
    path = os.path.abspath(path)
    if not path.startswith(os.path.abspath(working_directory)):
        return(f'Error: Cannot read "{file_path}" as it is outside the permitted working directory')
    elif not os.path.isfile(path):
        return(f'Error: File not found or is not a regular file: "{file_path}"')

    try:
        with open(path, 'r') as file:
            content = file.read()
            if len(content) > MAX_CHAR:
                content = content[:MAX_CHAR] + f"...File {file_path} truncated to 10000 characters]"
            return content
    except Exception as e:
        raise Exception(f'Error: {e}')
    return None