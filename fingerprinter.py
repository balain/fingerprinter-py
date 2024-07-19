import hashlib
import json
import os
import os.path
import sys
from datetime import datetime
import pprint
from simple_chalk import chalk, green, red, yellow
import time

start_time = time.time()

os.system('color')  # necessary to print color text to the windows terminal - https://stackoverflow.com/a/293633

EXCLUDE_LIST = []
# EXCLUDE_LIST = ['.fingerprint-data', '.git', '.idea', '.venv', 'bin', 'Include', 'lib', 'Lib', 'Scripts', 'out.json']

DATA_DIR = ".fingerprint-data"

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

# def main(directory, json_file="out.json"):

def main(directory=".", json_file="out"):
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
    main(sys.argv[1], sys.argv[2])
    print('Execution time: ', time.time() - start_time, ' seconds')