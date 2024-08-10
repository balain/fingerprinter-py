# Fingerprinter (Python)

Take fingerprints (md5) of files in specified folder, recursively. 

Optionally:
- Compare with previous snapshots and report on any changes (i.e. added, changed, or deleted files).
- Run a continuous watch, cycling every 600sec (configurable).

## Quick Start

Clone the repo and run the file using all defaults. The current folder will be scanned and the output (json) file (`output.json`) will be saved in the `.fingerprint-data` folder:

```bash
$ git clone https://github.com/balain/fingerprinter-py.git
$ python fingerprinter.py
$ cat .fingerprint-data/output.json
```

## Getting Started

### Prerequisites

The things you need before installing the software:

* Python3
* venv (optional but recommended)

### Installation

To run this program:

```bash
$ git clone https://github.com/balain/fingerprinter-py.git
```

## Options

Using argparse

```bash
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Path to scan (default: ".")
  -o OUTPUT, --output OUTPUT
                        Output json file (default: "output.json")
  -d DATA_DIR, --data-dir DATA_DIR
                        Data directory (where the json file is saved; default: ".fingerprint-data")
  -x EXCLUDE, --exclude EXCLUDE
                        Folders to exclude (default: ['.git', '.venv', '.idea', 'bin', 'Include', 'include', 'Lib', 'lib', 'Scripts', 'scripts', 'out.json'])
  -w, --watch           Watch for changes and update output json
  -t WATCH_PERIOD, --watch-period WATCH_PERIOD
                        How many seconds to wait between scans (default 600)
  -v, --verbose         Verbose output
```

## Usage

A few examples of useful commands and/or tasks:

### Use defaults

Scan the current folder:

```bash
$ python fingerprinter.py
```

### Using additional parameters

Scan the current folder, exclude .git folder(s), output to parent.json in the output-files folder (created if it doesn't already exist):

```bash
$ python fingerprinter.py -p .. -x git -o parent.json -d output-files
```

## Sample Output

Run it again, saving it to `./junk/junk.json`; Exclude `gi`, `gii`, and `git` files/folders.

The output shows two new files, no deleted files, and two changed files, including the python source file. It also shows the prior and latest timestamps (in the `meta` object).

```bash
❯ python fingerprinter.py -p . -o junk -d junk -x gi -x gii -x git
MD5 checksums saved to junk/junk.json
{'new': ['junk/junk-latest-diff.json', 'junk/junk-1723254528-diff.json'],
 'deleted': [],
 'changed': ['fingerprinter.py', 'junk/junk.json'],
 'meta': {'old': '2024-08-09T21:48:48', 'new': '2024-08-09T21:50:01'}}
```

## TODOs

- Implement alternative (optional) sqlite storage

## Other Similar or Related Projects

- [fingerprinter-rs](https://github.com/balain/fingerprinter-rs): Rust port (fewer features but much (!) faster).
- [fingerprinter](https://github.com/balain/fingerprinter): Original Typescript version. No longer maintained.
