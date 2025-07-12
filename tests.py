from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content

def test_get_files_info(working_directory, directory=None):
    try:
        files_info = get_files_info(working_directory, directory)
        return files_info
    except Exception as e:
        return str(e)

def print_files_info(files_info, working_directory, directory=None):
    if directory == ".":
        print(f"Result for the current directory:")
    else:
        print(f"Result for '{directory}' directory:")
    if isinstance(files_info, str):
        print("    "+ files_info)
    else:
        for file in files_info:
            print(" " +file)

def main():
    contents = get_file_content("calculator", "main.py")
    print("Content of 'main.py':")
    print(contents)

    contents = get_file_content("calculator", "pkg/calculator.py")
    print("\nContent of 'pkg/calculator.py':")
    print(contents)

    contents = get_file_content("calculator", "/bin/cat.py")
    print("\nContent of '/bin/cat.py':")
    print(contents)

if __name__ == "__main__":
    main()