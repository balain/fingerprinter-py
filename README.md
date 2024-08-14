# Fingerprinter (Python)

Take fingerprints (md5) of files in specified folder, recursively or website(s).

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

Clone the repo and install the required modules:

```bash
$ git clone https://github.com/balain/fingerprinter-py.git
$ pip install -r requirements.txt
```

## Options

Using argparse

```bash
❯ python fingerprinter.py --help
usage: fingerprinter.py [-h] [-p PATH] [-o OUTPUT] [-c] [-d DATA_DIR] [-a] [-t] [-x EXCLUDE] [-u URL] [-w] [-wp WATCH_PERIOD] [-s SQLITE_FILENAME] [-v]

options:
  -h, --help            show this help message and exit
  -p PATH, --path PATH  Path to scan (default: "None")
  -o OUTPUT, --output OUTPUT
                        Output json file (not including extension; default: "output")
  -c, --cache           Cache website snapshot(s)
  -d DATA_DIR, --data-dir DATA_DIR
                        Data directory (where the json file is saved; default: ".fingerprint-data")
  -a, --audio           Enable audio feedback (beep on change)
  -t, --timing          Capture execution time
  -x EXCLUDE, --exclude EXCLUDE
                        Folders to exclude (default: ['.git', '.venv', '.idea', 'bin', 'Include', 'include', 'Lib', 'lib', 'Scripts', 'scripts', 'output.json'])
  -u URL, --url URL     URL(s) to fetch
  -w, --watch           Watch for changes and update output json
  -wp WATCH_PERIOD, --watch-period WATCH_PERIOD
                        How many seconds to wait between scans (default 600)
  -s SQLITE_FILENAME, --sqlite-filename SQLITE_FILENAME
                        Filename to save output to sqlite database (default: unset)
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

#### Specify output file

Scan the current folder, exclude .git folder(s), output to parent.json in the output-files folder (created if it doesn't already exist):

```bash
$ python fingerprinter.py -p .. -x git -o parent.json -d output-files
```

#### Fingerprint URL(s)

Fetch the URL(s) provided and output to websites.json every 30 seconds:

```bash
$ python fingerprinter.py -u https://www.ibm.com -u https://www.apple.com -u https://www.ubuntu.com -w -wp 30 -o websites
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

## Features

## Implemented
- [x] Implement alternative (optional) sqlite storage
- [x] Fingerprint URLs
- [x] Generate sample timings
- [x] Cache websites
- [x] Audio feedback on change

## TODOs

- [ ] Implement diff calculation with sqlite database
- [ ] Optimize sqlite updates (e.g. batch/chunk if > some large threshold)

## Other Similar or Related Projects

- [fingerprinter-rs](https://github.com/balain/fingerprinter-rs): Rust port (uses sha256; fewer features but much (!) faster).
- [fingerprinter](https://github.com/balain/fingerprinter): Original Typescript version. No longer maintained.

## License

MIT - https://mit-license.org

Copyright &copy; 2024 John D. Lewis

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.