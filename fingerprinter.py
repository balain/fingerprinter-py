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

EXCLUDE_LIST_DEFAULT = ['.git', '.venv', '.idea', 'bin', 'Include', 'include', 'Lib', 'lib', 'Scripts', 'scripts', 'output.json']

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", help='Path to scan (default: "%(default)s")', default=".", required=True)
parser.add_argument("-o", "--output", help='Output json file (not including extension; default: "%(default)s")', default="output" )
parser.add_argument("-d", "--data-dir", help='Data directory (where the json file is saved; default: "%(default)s")', default=".fingerprint-data")
parser.add_argument("-t", "--timing", help='Capture execution time', action='store_true', default=False)
parser.add_argument("-x", "--exclude", help='Folders to exclude (default: %(default)s)', action='append', default=EXCLUDE_LIST_DEFAULT)
parser.add_argument("-w", "--watch", help="Watch for changes and update output json", action='store_false', default=False)
parser.add_argument("-wp", "--watch-period", default=600, help='How many seconds to wait between scans (default %(default)i)', type=int)
parser.add_argument("-s", "--sqlite-filename", help="Filename to save output to sqlite database (default: unset)")
parser.add_argument("-v", "--verbose", help="Verbose output",action='store_true', default=False)

args = parser.parse_args()

# Set up timing, if requested
if args.timing:
    print(yellow('Capturing execution time'))
    import time
    start_time = time.time()

# Set up exclude list
EXCLUDE_LIST = args.exclude

# Set up database, if selected
if args.sqlite_filename:
    print(f"Saving output to sqlite database: {args.sqlite_filename}")
    import sqlite3
    connection = sqlite3.connect(args.sqlite_filename)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS fingerprints (path text, md5 text, created text)")
    cursor.execute("DELETE FROM fingerprints")
    connection.commit()
    dbdata = []

# sys.exit(10)

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
        # Skip the file if encountering some permission error (e.g. with OneDrive files)
        print(yellow.dim(f"ERR: Permission error caught with {file_path}... ignoring"))
    except FileNotFoundError as fe:
        # Skip the file if it doesn't exist...
        print(red.dim(f"ERR: File not found error caught with {file_path}... ignoring"))
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

def save_md5_to_json(md5_dict, json_file):
    """Save the MD5 dictionary to a JSON file."""
    with open(json_file, 'w') as f:
        json.dump(md5_dict, f, indent=4)

def save_md5_to_sqlite(md5_dict, connection, cursor):
    """Save the MD5 dictionary to a SQLite database."""
    save_timestamp = md5_dict['meta']['updated_on']['b']

    for f in md5_dict['files']:
        dbdata.append((f, md5_dict['files'][f], save_timestamp))

    cursor.executemany("INSERT INTO fingerprints (path, md5, created) VALUES (?, ?, ?)", dbdata)
    connection.commit()

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

    if args.sqlite_filename:
        print(green(f"Saving to SQLite database: {args.sqlite_filename}"))
        save_md5_to_sqlite(md5_dict, connection, cursor)
    else:
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
                # pprint.pprint(changes)
                # winsound.Beep(2500, 100)
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
            for remaining in range(args.watch_period, 0, -1):
                sys.stdout.write("\r")
                sys.stdout.write("{:2d} seconds remaining.".format(remaining))
                sys.stdout.flush()
                time.sleep(1)
    else:
        main(dir_name, json_name)
        # Print execution time, if requested
        if args.timing:
            print(yellow(f'Execution time: {time.time() - start_time} seconds'))