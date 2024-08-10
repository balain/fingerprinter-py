# Project Title

Capture fingerprints (md5) of files in specified folder, recursively. 

Optionally:
- Compare with previous snapshots and report on any changes (i.e. added, changed, or deleted files).
- Run a continuous watch, cycling every 600sec (configurable).

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

### TODOs

- Implement alternative (optional) sqlite storage