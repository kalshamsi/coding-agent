from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python_file import run_python_file

def main():
    """print(write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum"))
    print(get_file_content("calculator", "lorem.txt"))

    print(write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet"))
    print(get_file_content("calculator", "pkg/morelorem.txt"))

    print(write_file("calculator", "/tmp/temp.txt", "this should not be allowed"))
    print(get_file_content("calculator", "/tmp/temp.txt"))"""

    print(run_python_file("calculator", "main.py"))
    print(run_python_file("calculator", "tests.py"))
    print(run_python_file("calculator", "../main.py"))
    print(run_python_file("calculator", "nonexistent.py"))

if __name__ == "__main__":
    main()