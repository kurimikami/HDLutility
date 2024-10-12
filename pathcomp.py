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
    file_cnt = 0
    ext_pattern = r"(?<=[$/\w\W])\s*([^'\"\[\];\s]+\.(vhd|v|sv|svh))\b"
    # ext_pattern = r"(?:\s*[=|'|\"|\[|+]\s*)([^'\"=\s]+\.(?:vhd|sv|v|svh))\b(?:\s*\w*)"

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
                        paths[basename] = {'LN': '\(' + str(linenum).rjust(10) + '\)', 'PATH': resolve_symlink(fullpath, expand)}
                        file_cnt += 1
    except IOError as e:
        print(f"Error: Unable to read file '{filename}'. {str(e)}")

    return [file_cnt, paths]

# Display the differences
def compare_paths(paths_a, paths_b):
    matched_cnt = 0
    UM_cnt = 0
    xA_cnt = 0
    xB_cnt = 0

    for basename in list(paths_b.keys()):
        if paths_a.get(basename, None):
            if paths_a[basename]['PATH'] != paths_b[basename]['PATH']:
                print(Black + '#UM A :' + paths_a[basename]['LN'] + ' ' + paths_a[basename]['PATH'])
                print(Red   + '#UM B :' + paths_b[basename]['LN'] + ' ' + paths_b[basename]['PATH'])
                UM_cnt += 1
            else:
                matched_cnt += 1
        else:
            print(Cyan + '#xA B ', paths_b[basename]['PATH'])
            xA_cnt += 1

    for basename in list(paths_a.keys()):
        if basename not in paths_b:
            print(Black + '#xB A ', paths_a[basename]['PATH'])
            xB_cnt += 1

    return [matched_cnt, UM_cnt, xA_cnt, xB_cnt]

# Export information from file A
def export_paths(paths_a):
    # print("Paths of files listed in file A:")
    for basename, fullpath in paths_a.items():
        print(paths_a[basename]['LN'] + ' ' + paths_a[basename]['PATH'])


def check_existence(paths_a,dir_path):
    paths = {}
    matched_cnt = 0
    NF_cnt = 0

    found_files = find_files(dir_path, {'.vhd', '.v', '.svh', '.sv'})

    for path in found_files:
        paths[os.path.basename(path)] = path
    for basename, fullpath in paths_a.items():
        if basename not in found_files:
            print(Red   + '#NF A :' + paths_a[basename]['LN'] + ' ' + paths_a[basename]['PATH'])
            NF_cnt += 1
            if paths.get(basename, None):
                print(Black   + '#EX ? :          ' +  ' ' + paths[basename])
        else:
            matched_cnt += 1

    return [matched_cnt, NF_cnt]

# Main function
def main():
    parser = argparse.ArgumentParser(description="File PATH comparison tool")
    parser.add_argument('file_a', help='file A')
    parser.add_argument('file_b', nargs='?', help='file B', default=None)
    parser.add_argument('--export', action='store_true', help='print paths of file A')
    parser.add_argument('--expand', action='store_true', help='expand environment variables in file paths of file A')
    parser.add_argument('--check', nargs='?', const=os.getcwd(), help='check if paths exist in specified directory')
    
    args = parser.parse_args()
    expand = args.expand or args.check
    
    # Create a PATH list for file A
    path_cnt_a, paths_a = read_paths(args.file_a, expand)

    if args.export:
        # If --export is specified, export only the paths from file A
        export_paths(paths_a)
                
        print("-------------------------------------------------------------")
        print("The " + str(path_cnt_a).rjust(6) + " paths were found in " +  args.file_a)

        if args.check:
            matched_cnt, NF_cnt = check_existence(paths_a, args.check)

            print("-------------------------------------------------------------")
            print("The " + str(path_cnt_a).rjust(6) + " paths were found in " + args.file_a)
            print("Matched  : " + str(matched_cnt))
            print("Not Found files under ./ : " + str(NF_cnt))

        else:
            # If --export is not specified, compare file A with file B
            if args.file_b:
                path_cnt_b, paths_b = read_paths(args.file_b, expand)
                matched_cnt, UM_cnt, xA_cnt, xB_cnt = compare_paths(paths_a, paths_b)

                print("-------------------------------------------------------------")
                print("The " + str(path_cnt_a).rjust(6) + " paths were found in " + args.file_a)
                print("The " + str(path_cnt_b).rjust(6) + " paths were found in " + args.file_b)
                print("Matched  　: " + str(matched_cnt).rjust(6))
                print("UnMatched　: " + str(UM_cnt).rjust(6))
                print("Not Exsit in " + args.file_a + ':' + str(xA_cnt).rjust(6))
                print("Not Exsit in " + args.file_b + ':' + str(xB_cnt).rjust(6))
            else:
                print("Error")
                parser.print_usage()

if __name__ == "__main__":
    main()