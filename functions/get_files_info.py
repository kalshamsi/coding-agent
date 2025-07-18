import os

def get_files_info(working_directory, directory=None):
    if directory is None or directory == "":
        directory = "."
    path = os.path.join(working_directory, directory)
    path = os.path.abspath(path)
    if not path.startswith(os.path.abspath(working_directory)):
        return (f'Error: Cannot list "{directory}" as it is outside the permitted working directory.')
    
    if not os.path.isdir(path):
        return (f'Error: "{directory}" is not a directory.')
    
    try:
        files = os.listdir(path)
    except Exception as e:
        raise Exception(f'Error: {e}')
    
    file_info = []
    try:
        for file in files:
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                file_info.append({'name': file, 'size': size, 'is_dir': False})
            elif os.path.isdir(file_path):
                size = sum(os.path.getsize(os.path.join(file_path, f)) for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, f)))
                file_info.append({'name': file, 'size': size, 'is_dir': True})
    except Exception as e:
        raise Exception(f'Error: {e}')

    #create a return string in the following format:
    #- <name>: file_size=<file_size> bytes, is_dir=<is_dir> for all files in file_info
    return_string = []
    for file in file_info:
        return_string.append(f"- {file['name']}: file_size={file['size']} bytes, is_dir={file['is_dir']}")
    return "\n".join(return_string) if return_string else "No files found."