#!/bin/python3
import argparse
import re
import os

# Remove comments, backslashes, and whitespace
def clean_path(line):
    # Remove comments
    line = re.sub(r'#.*|//.*', '', line)  # Remove everything after '#' or '//'
    line = re.sub(r'/\*.*?\*/', '', line, flags=re.DOTALL)  # Remove '/* */' comments
    line = re.sub(r"\$::env\((\w+)\)", r"${\1}", line, flags=re.DOTALL)
    line = line.replace('\\', '')  
    return line

def resolve_symlink(path):
    """
    Follows the nesting of symbolic links, expands environment variables if present,
    and returns the final target file path.
    """
    try:
        # Expand environment variables
        expanded_path = os.path.expandvars(path)
        # Get the actual path that the link ultimately points to (file/directory)
        real_path = os.path.realpath(expanded_path)
        return real_path
    except Exception as e:
        return str(e)

# Read the file and create a cleaned-up PATH list
def read_paths(filename):
    paths = {}
    linenum = 0
    # ext_pattern = r"(?<=[$/\w\W])\s*([^'\"\[\];\s]+\.(vhd|v|sv|svh))\b"
    ext_pattern = r"(?:\s*[=|'|\"|\[|+]\s*)([^'\"=\s]+\.(?:vhd|sv|v|svh))\b(?:\s*\w*)"
    
    with open(filename, 'r') as file:
        for line in file:
            linenum += 1
    
            fullpaths = re.findall(ext_pattern, clean_path(line))
            if fullpaths:
                for fullpath in fullpaths :
                    filename = os.path.basename(fullpath)
                    paths[filename] = {'LN': str(linenum).rjust(10), 'PATH': resolve_symlink(fullpath)}

    return paths

# Display the differences
def compare_paths(paths_a, paths_b):
    Black = "\033[0m"
    Red   = "\033[31m"
    for filename, fullpath in paths_b.items():
        filename = paths_a.get('PATH', {}).get('PATH', None)
        if filename:
            if paths_a[filename]['PATH'] != paths_b[filename]['PATH']:
                print(Black + '#UM A :' + paths_a[filename]['LN'] + ' ' + paths_a[filename]['PATH'])
                print(Red   + '#UM B :' + paths_b[filename]['LN'] + ' ' + paths_b[filename]['PATH'])
        else:
            print('#xA B ', paths_b[filename]['PATH'])
    for filename, fullpath in paths_a.items():
        if filename not in paths_b:
            print('#xB A ', paths_a[filename]['PATH'])

# Export information from file A
def export_paths(paths_a):
    # print("Paths of files listed in file A:")
    for filename, fullpath in paths_a.items():
        print(paths_a[filename]['LN'] + ' ' + paths_a[filename]['PATH'])

# Main function
def main():
    parser = argparse.ArgumentParser(description="File PATH comparison tool")
    parser.add_argument('file_a', help='file A')
    parser.add_argument('file_b', nargs='?', help='file B', default=None)
    parser.add_argument('--export', action='store_true', help='print paths of file A')
    
    args = parser.parse_args()

    # Create a PATH list for file A
    paths_a = read_paths(args.file_a)

    if args.export:
        # If --export is specified, export only the paths from file A
        export_paths(paths_a)
    else:
        # If --export is not specified, compare file A with file B
        if args.file_b:
            paths_b = read_paths(args.file_b)
            compare_paths(paths_a, paths_b)
        else:
            print("Error")

if __name__ == "__main__":
    main()