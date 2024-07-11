import hashlib
import json
import os
import os.path
import pprint
import sys
from datetime import datetime
from simple_chalk import green, yellow

os.system('color')  # necessary to print color text to the windows terminal - https://stackoverflow.com/a/293633

EXCLUDE_LIST = ['.git', '.venv', '.idea', 'Include', 'Lib', 'Scripts', 'out.json']

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

def save_md5_to_json(md5_dict, json_file="out.json"):
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

def main(directory=".", json_file="out.json"):
    # directory = input("Enter the directory path to calculate MD5 sums: ")
    # json_file = input("Enter the output JSON file path: ")
    md5_dict = get_files_md5(directory)
    print(green(f"MD5 checksums saved to {json_file}"))
    if os.path.isfile(json_file):
        old_dict = read_md5_from_json(json_file)
        changes = compare_data(old_dict, md5_dict)
        changes['meta'] = {}
        changes['meta']['old'] = old_dict['meta']['updated_on']['a']
        changes['meta']['new'] = md5_dict['meta']['updated_on']['a']
        if (len(changes['new']) + len(changes['deleted']) + len(changes['changed']) == 0):
            print('No changes')
        else:
            pprint.pp(changes)
    else:
        print("Old file doesn't exist, so skipping comparison.")
    save_md5_to_json(md5_dict, json_file)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
