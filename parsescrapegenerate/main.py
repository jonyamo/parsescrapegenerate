# -*- coding: utf-8 -*-

"""
parsescrapegenerate.main
--------------------

Main entry point for ParseScrapeGenerate.
"""
import feedparser
import time

from . import __title__, __version__
from .feed import get_feed

def parse(feed):
    """
    Parse the given feed.
    """
    return feedparser.parse(feed)


def scrape(feed_config, input_feed={}):
    """
    Scrape the link from the feed config, using the defined rules to extract
    entries. If an optional input feed is given, extract the entries from it
    and add them to the resulting scraped feed.
    """
    if 'format' in feed_config:
        format = feed_config['format']
    else:
        format = 'rss'

    entry_tags = []
    input_entries = input_feed.get('entries', [])
    for entry in input_entries:
        entry_tags.append(entry['id'])

    feed = get_feed(format)
    feed.generator = '{0} {1}'.format(__title__, __version__)
    feed.link = feed_config['path']
    feed.title = feed.fetch_val('title', feed_config, input_feed.get('feed', {}))
    feed.lang = feed.fetch_val('lang', feed_config, input_feed.get('feed', {}))
    feed.entries = feed.fetch_entries(feed_config['entry'], entry_tags)
    if len(feed.entries) > len(entry_tags):
        time_struct=time.gmtime()
    else:
        try:
            time_struct=input_feed['feed']['updated_parsed']
        except Exception as e:
            time_struct=time.gmtime()
    feed.updated = feed.get_date(time_struct)

    return feed


def generate(feed):
    """
    Return the given feed object as XML.
    """
    return feed.xml()
