# -*- coding: utf-8 -*-

"""
parsescrapegenerate.feed
------------------------

Feed related functions for ParseScrapeGenerate.
"""
import os
import requests
import time

from lxml import html
try:
    from urllib.parse import urlparse
except:
    from urlparse import urlparse

from .exceptions import FeedPathDoesNotExist, InvalidFeedFormat
from .utils import get_clean_html, lazyattr, render_template

def get_feed(format='rss'):
    """
    The feed factory.
    """
    feeds = {'atom':AtomFeed,'rss':RssFeed}
    if format in feeds:
        return feeds[format]()
    else:
        raise InvalidFeedFormat


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

    @lazyattr
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
            title = self.tree.xpath('//title/text()')[0]
            return title.strip()
        except:
            return ''

    def fetch_lang(self):
        try:
            lang = self.tree.xpath('/html/@lang')[0]
            return lang.strip()
        except:
            return ''

    def fetch_entries(self, config, existing_ids=[]):
        entries = []
        templates = config.get('templates', [])

        # try:
        for node in self.tree.xpath(config['xpath']['context']):
            vals = {}
            for key, value in config['xpath'].items():
                if key == 'context':
                    continue
                try:
                    elem = node.xpath(value)[0]
                    vals[key] = get_clean_html(elem)
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
        # except Exception as e:
        #     pass

        return entries

    def get_date(self, time_struct=time.gmtime()):
        try:
            return time.strftime(self.DATE_FORMAT, time_struct)
        except Exception as e:
            return ''

    def xml(self):
        return render_template(self.TEMPLATE_FILE, {'feed': self})


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
            return render_template(templates[attr], {'entry': vals})
        elif attr in vals:
            return vals[attr]
        else:
            return ''
