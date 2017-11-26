# py-epubber

This script generates an epub book from either a Wordpress blog or a set of URLs. It is originally derived from https://github.com/rdeits/WPepub but has been heavily modified.

## Setup

1. This is only tested with Python 2.7.
1. Make sure you have `pandoc` installed:
```
brew install pandoc
```
1.
```
pip install -r requirements.txt
```

## Usage

    ./epubber.py -c <yaml filename>

This will create a new epub in `build/<filename-without-.yaml>.epub`.

It will also cache the downloaded pages in `rst-<filename-without-.yaml>` so subsequent runs do not need to redownload them.
