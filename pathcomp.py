#!/bin/python3
import argparse
import re
import os

Black  = "\033[0m"
Red    = "\033[31m"
Yellow = "\033[33m"
Cyan   = "\033[36m"

# Remove comments, backslashes, and whitespace
def clean_path(line):
    # Remove comments
    line = re.sub(r'#.*|//.*', '', line)  # Remove everything after '#' or '//'
    line = re.sub(r'/\*.*?\*/', '', line, flags=re.DOTALL)  # Remove '/* */' comments
    line = re.sub(r"\$::env\((\w+)\)", r"${\1}", line, flags=re.DOTALL)
    line = line.replace('\\', '')  
    return line

def find_files(directory, extensions = {'.vhd', '.v', '.svh', '.sv'}):
    found_files = []

    for root, dirs, files in os.walk(directory):
        for filename in files:
            if os.path.splitext(filename)[1] in extensions:
                found_files.append(resolve_symlink(os.path.join(root, filename)))

    return found_files

def resolve_symlink(path, expand=False):
    try:
        # Expand environment variables
        if expand:
            path = os.path.expandvars(path)
        # Get the actual path that the link ultimately points to (file/directory)
        real_path = os.path.realpath(path)
        return real_path
    except Exception as e:
        return str(e)

# Read the file and create a cleaned-up PATH list
def read_paths(filename, expand=False):
    paths = {}
    linenum = 0
    # ext_pattern = r"(?<=[$/\w\W])\s*([^'\"\[\];\s]+\.(vhd|v|sv|svh))\b"
    ext_pattern = r"(?:\s*[=|'|\"|\[|+]\s*)([^'\"=\s]+\.(?:vhd|sv|v|svh))\b(?:\s*\w*)"

    if not os.path.exists(filename):
        print(f"Error: File '{filename}' does not exist.")
        return paths
    
    try:
        with open(filename, 'r') as file:
            for line in file:
                linenum += 1
        
                fullpaths = re.findall(ext_pattern, clean_path(line))
                if fullpaths:
                    for fullpath in fullpaths :
                        basename = os.path.basename(fullpath)
                        if basename in paths :
                            print(Yellow + '#REPL : ' + Black + basename + '(' + filename + ')')
                        paths[filename] = {'LN': str(linenum).rjust(10), 'PATH': resolve_symlink(fullpath, expand)}
    except IOError as e:
        print(f"Error: Unable to read file '{filename}'. {str(e)}")

    return paths

# Display the differences
def compare_paths(paths_a, paths_b):
    for filename in list(paths_b.keys()):
        filename = paths_a.get('PATH', {}).get('PATH', None)
        if filename:
            if paths_a[filename]['PATH'] != paths_b[filename]['PATH']:
                print(Black + '#UM A :' + paths_a[filename]['LN'] + ' ' + paths_a[filename]['PATH'])
                print(Red   + '#UM B :' + paths_b[filename]['LN'] + ' ' + paths_b[filename]['PATH'])
        else:
            print(Cyan + '#xA B ', paths_b[filename]['PATH'])

    for filename in list(paths_a.keys()):
        if filename not in paths_b:
            print(Black + '#xB A ', paths_a[filename]['PATH'])

# Export information from file A
def export_paths(paths_a):
    # print("Paths of files listed in file A:")
    for filename, fullpath in paths_a.items():
        print(paths_a[filename]['LN'] + ' ' + paths_a[filename]['PATH'])

def check_existence(paths_a):
    found_files = find_files(os.getcwd(), {'.vhd', '.v', '.svh', '.sv'})
    for filename, fullpath in paths_a.items():
        if filename not in found_files:
            print(Red   + '#NF A :' + paths_a[filename]['LN'] + ' ' + paths_a[filename]['PATH'])

# Main function
def main():
    parser = argparse.ArgumentParser(description="File PATH comparison tool")
    parser.add_argument('file_a', help='file A')
    parser.add_argument('file_b', nargs='?', help='file B', default=None)
    parser.add_argument('--export', action='store_true', help='print paths of file A')
    parser.add_argument('--expand', action='store_true', help='expand environment variables in file paths')
    parser.add_argument('--check', action='store_true', help='check if paths exist in current directory')
    
    args = parser.parse_args()
    expand = args.expand or args.check
    
    # Create a PATH list for file A
    paths_a = read_paths(args.file_a, expand)

    if args.export:
        # If --export is specified, export only the paths from file A
        export_paths(paths_a)
        
        if args.check:
            check_existence(paths_a)

        else:
            # If --export is not specified, compare file A with file B
            if args.file_b:
                paths_b = read_paths(args.file_b, expand)
                compare_paths(paths_a, paths_b) 
            else:
                print("Error")
                parser.print_usage()

if __name__ == "__main__":
    main()