# -*- coding: utf-8 -*-

"""
ParseScrapeGenerate. Parse, scrape, and generate feeds.

Usage: parsescrapegenerate <config_path>

Arguments:
    config_path  Path to a feed config file

Options:
    -h --help    Show help
    --version    Show version

Once invoked, parsescrapegenerate will load config_path, scrape the given site
looking for entries matching the defined rules. Once all the data is collected
the resulting XML data will be written to STDOUT. Existing XML data can be read
from STDIN, in which case, all entries will be extracted and added to the
resulting output (duplicates will be ignored).

"""
import docopt
import os
import sys

from . import __version__
from .config import get_config
from .main import parse, scrape, generate

def main():
    args = docopt.docopt(__doc__, version=__version__)
    feed_config = get_config(args['<config_path>'])
    input_feed = parse(sys.stdin.read()) if not os.isatty(0) else {}
    new_feed = scrape(feed_config, input_feed)
    print(generate(new_feed))


if __name__ == '__main__':
    main()

