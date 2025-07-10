from functions.get_files_info import get_files_info

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
    # test 1
    files_info = test_get_files_info('calculator', '.')
    print_files_info(files_info, 'calculator', '.')

    # test 2
    files_info = test_get_files_info('calculator', 'pkg')
    print_files_info(files_info, 'calculator', 'pkg')

    # test 3
    files_info = test_get_files_info('calculator', '/bin')
    print_files_info(files_info, 'calculator', '/bin')

    # test 4
    files_info = test_get_files_info('calculator', '..')
    print_files_info(files_info, 'calculator', '..')


if __name__ == "__main__":
    main()