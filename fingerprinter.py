import hashlib
import json
import os
import os.path
import sys
from datetime import datetime
import pprint
from simple_chalk import chalk, green, red, yellow
#import winsound
import time
import platform

import argparse

EXCLUDE_LIST_DEFAULT = ['.git', '.venv', '.idea', 'bin', 'Include', 'include', 'Lib', 'lib', 'Scripts', 'scripts', 'out.json']

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", default=".", help='Path to scan (default: "%(default)s")', required=True)
parser.add_argument("-o", "--output", default="output.json", help='Output json file (default: "%(default)s")')
parser.add_argument("-d", "--data-dir", default=".fingerprint-data", help='Data directory (where the json file is saved; default: "%(default)s")')
parser.add_argument("-x", "--exclude", help='Folders to exclude (default: %(default)s)', action='append', default=EXCLUDE_LIST_DEFAULT)
parser.add_argument("-w", "--watch", action='store_false', default=False, help="Watch for changes and update output json")
parser.add_argument("-t", "--watch-period", default=600, help='How many seconds to wait between scans (default %(default)i)', type=int)
parser.add_argument("-v", "--verbose", action='store_true', default=False, help="Verbose output")

args = parser.parse_args()

EXCLUDE_LIST = args.exclude

# print(f"args: {args}")
# print("git" in args.exclude)
# exit(100)

# Set up console colors
if platform.system() == 'Windows':
    os.system('color')  # necessary to print color text to the windows terminal - https://stackoverflow.com/a/293633

# Set up global variables
DATA_DIR = args.data_dir

# Create data directory if it doesn't exist already
if (not os.path.isdir(DATA_DIR)):
    os.makedirs(DATA_DIR)

def calculate_md5(file_path):
    """Calculate the MD5 checksum of a file."""
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            # Read and update hash in chunks to handle large files
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
    except PermissionError as pe:
        # print(colored(f"ERR: Permission error caught with {file_path}... ignoring", 'red'))
        print(yellow.dim(f"ERR: Permission error caught with {file_path}... ignoring"))
    return hasher.hexdigest()

def get_files_md5(directory):
    """Recursively calculate MD5 for all files in the directory."""
    # print(f"Processing dir: {directory}...")
    md5_dict = {}
    response = {}
    for (root, dirs, files) in os.walk(directory, topdown=True):
        if not exclude_dir(directory, root):
            # print(f"Root: {root}...")
            # print(f"{root}\t{dirs}\t{files}...")
            for file in files:
                if file not in EXCLUDE_LIST:
                    # print(f"Processing {file}...root: {root}... subdir: {root[len(directory)+1:]}")
                    file_path = os.path.join(root, file)
                    md5_dict[os.path.join(root[len(directory) + 1:], file)] = calculate_md5(file_path)
    now = datetime.now()
    response['meta'] = {'path': directory,
                        'updated_on': {'a': now.strftime("%Y-%m-%dT%H:%M:%S"), 'b': int(now.timestamp())}}
    response['files'] = md5_dict
    return response

def compare_data(old_data, new_data):
    changes = {}
    changes['new'] = []
    changes['deleted'] = []
    changes['changed'] = []
    if old_data['files'] != new_data['files']:
        changes = {'new': [], 'deleted': [], 'changed': []}
        for f in old_data['files']:
            if f not in new_data['files']:
                changes['deleted'].append(f)
            else:  # m5s match?
                if old_data['files'][f] != new_data['files'][f]:
                    changes['changed'].append(f)
        for f in new_data['files']:
            if f not in old_data['files']:
                changes['new'].append(f)
    return changes

def in_json(data, filename):
    return (filename in data)

def read_md5_from_json(filename):
    old_dict = {}
    try:
        with open(filename, 'r') as f:
            old_dict = json.load(f)
    except FileNotFoundError as fnfex:
        print(f"Couldn't find {filename}... ignoring")
    return old_dict

def save_md5_to_json(md5_dict, json_file="out"):
    """Save the MD5 dictionary to a JSON file."""
    with open(json_file, 'w') as f:
        json.dump(md5_dict, f, indent=4)

def exclude_dir(directory, root):
    # print(f"exclude_dir({directory}, {root}) ...")
    for excl in EXCLUDE_LIST:
        # print("Root substr and excl", root[len(directory)+1:len(directory)+len(excl)+1], excl)
        if root[len(directory) + 1:len(directory) + len(excl) + 1] == excl:
            return True
    return False

def main(directory, json_file):
    global DATA_DIR
    # directory = input("Enter the directory path to calculate MD5 sums: ")
    # json_file = input("Enter the output JSON file path: ")
    json_filename = get_filename_json_root(json_file)
    md5_dict = get_files_md5(directory)
    print(green(f"MD5 checksums saved to {json_filename}"))
    if os.path.isfile(json_filename):
        old_dict = read_md5_from_json(json_filename)
        changes = compare_data(old_dict, md5_dict)
        changes['meta'] = {}
        changes['meta']['old'] = old_dict['meta']['updated_on']['a']
        changes['meta']['new'] = md5_dict['meta']['updated_on']['a']
        json_base = get_filename_root(json_file + "-" + str(md5_dict['meta']['updated_on']['b']))
        # No changes
        if (len(changes['new']) + len(changes['deleted']) + len(changes['changed']) == 0):
            print('No changes')
        else:  # Capture the changes
            # Save diffs to snapshot and "-latest" JSON files
            with open(get_filename_root(json_file + "-latest-diff.json"), 'w') as f:
                json.dump(changes, f)
            with open(json_base + "-diff.json", "w") as f:
                json.dump(changes, f)
            pprint.pp(changes)
            #winsound.Beep(2500, 100)
    else:
        print("Old file doesn't exist, so skipping comparison.")

    # Save full data to base JSON file - whether there were changes or not
    save_md5_to_json(md5_dict, get_filename_root(json_file) + ".json")

def get_filename_root(filename_root="data"):
    global DATA_DIR
    return (os.path.join(DATA_DIR, filename_root))

def get_filename_json_root(filename_root="data"):
    global DATA_DIR
    return (get_filename_root(filename_root) + ".json")

if __name__ == "__main__":
    dir_name = args.path
    json_name = args.output
    if args.watch:
        while True:
            main(dir_name, json_name)
            for remaining in range(600, 0, -1):
                sys.stdout.write("\r")
                sys.stdout.write("{:2d} seconds remaining.".format(remaining))
                sys.stdout.flush()
                time.sleep(1)
    else:
        main(dir_name, json_name)