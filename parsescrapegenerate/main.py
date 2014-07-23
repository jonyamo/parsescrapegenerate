# -*- coding: utf-8 -*-

"""
parsescrapegenerate.main
--------------------

Main entry point for ParseScrapeGenerate.
"""
import feedparser
import os
import re
import requests
import time

from jinja2 import Environment, PackageLoader, Template
from lxml import html
from lxml.html.clean import Cleaner
try:
    from urllib.parse import urlparse
except:
    from urlparse import urlparse

from . import __title__, __version__
from .exceptions import FeedPathDoesNotExist, InvalidFeedFormat

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

    feed = _get_feed(format)
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


def _get_feed(format='rss'):
    """
    The feed factory.
    """
    feeds = {'atom':AtomFeed,'rss':RssFeed}
    if format in feeds:
        return feeds[format]()
    else:
        raise InvalidFeedFormat


def _lazyattr(fn):
    """
    Lazy loaded attribute.
    http://stackoverflow.com/a/3013910
    """
    attr_name = '_lazy_' + fn.__name__

    @property
    def __lazyattr(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)

    return __lazyattr


class AbstractFeed:
    def __init__(self):
        if type(self) == 'AbstractFeed':
            raise Exception('AbstractFeed is abstract and cannot be instantiated.')

        self.id      = ''
        self.title   = ''
        self.updated = ''
        self.link    = ''
        self.lang    = ''
        self.entries = []

    @_lazyattr
    def cleaner(self):
        return Cleaner(safe_attrs_only=True, add_nofollow=True)

    @_lazyattr
    def template_env(self):
        return Environment(loader=PackageLoader(__title__.lower(), 'templates'))

    @_lazyattr
    def tree(self):
        tree = None
        o = urlparse(self.link)
        if o.scheme in ['http', 'https']:
            r = requests.get(self.link)
            r.raise_for_status()
            tree = html.fromstring(r.text)
        else:
            if not os.path.exists(self.link):
                raise FeedPathDoesNotExist
            tree = html.parse(self.link)
        return tree

    def fetch_val(self, attr, config, input_feed):
        if attr in config:
            return config[attr]
        elif attr in input_feed:
            return input_feed[attr]
        else:
            try:
                method = getattr(self, 'fetch_{}'.format(attr))
                return method()
            except Exception:
                return ''

    def fetch_title(self):
        try:
            title = self.tree.xpath('//title/text()')
            return title[0].strip()
        except:
            return ''

    def fetch_lang(self):
        try:
            lang = self.tree.xpath('/html/@lang')
            return lang[0].strip()
        except:
            return ''

    def fetch_entries(self, config, existing_ids=[]):
        entries = []
        templates = config.get('templates', [])

        try:
            for node in self.tree.xpath(config['xpath']['context']):
                vals = {}
                for key, value in config['xpath'].items():
                    if key == 'context':
                        continue
                    try:
                        elem = node.xpath(value)
                        vals[key] = self.clean_html(elem[0].strip())
                    except Exception as e:
                        vals[key] = ''

                entry = Entry()
                setattr(entry, 'title', entry.get_val('title', templates, vals))
                setattr(entry, 'link', entry.get_val('link', templates, vals))
                setattr(entry, 'content', entry.get_val('content', templates, vals))
                setattr(entry, 'published', self.get_date())
                setattr(entry, 'id', entry.generate_tag(self.DATE_FORMAT))

                if not entry.id in existing_ids:
                    entries.append(entry)
        except Exception as e:
            pass

        return entries

    def get_date(self, time_struct=time.gmtime()):
        try:
            return time.strftime(self.DATE_FORMAT, time_struct)
        except Exception as e:
            return ''

    def clean_html(self, html):
        """
        Remove malicious or improperly formatted html.
        http://stackoverflow.com/a/6450528
        """
        cleaned_html = self.cleaner.clean_html(html)
        return re.sub(r'</p>$', '', re.sub(r'^<p>', '', cleaned_html))

    def xml(self):
        template = self.template_env.get_template(self.TEMPLATE_FILE)
        return template.render(feed=self)


class AtomFeed(AbstractFeed):
    DATE_FORMAT='%Y-%m-%dT%H:%M:%SZ'
    TEMPLATE_FILE='atom.xml'


class RssFeed(AbstractFeed):
    DATE_FORMAT='%a, %d %b %Y %H:%M:%S Z'
    TEMPLATE_FILE='rss.xml'


class Entry:
    def __init__(self):
        self.id        = ''
        self.title     = ''
        self.updated   = ''
        self.published = ''
        self.link      = ''
        self.content   = ''

    def generate_tag(self, date_format):
        try:
            o = urlparse(self.link)
            pubdate = time.strftime('%Y-%m-%d',
                                    time.strptime(self.published, date_format))
            return 'tag:{netloc},{pubdate}:{path}'.format(
                netloc=o.netloc,pubdate=pubdate,path=o.path)
        except Exception as e:
            return ''

    def get_val(self, attr, templates, vals):
        if attr in templates:
            return Template(templates[attr]).render(entry=vals)
        elif attr in vals:
            return vals[attr]
        else:
            return ''
