# -*- coding: utf-8 -*-

"""
parsescrapegenerate.utils
-------------------------

Utility functions for ParseScrapeGenerate.
"""
import os
import re
import requests

from jinja2 import Environment, PackageLoader
from jinja2.exceptions import TemplateNotFound
from lxml import html
from lxml.html.clean import Cleaner
try:
    from urllib.parse import urlparse
except:
    from urlparse import urlparse

from . import __title__
from .exceptions import FeedPathDoesNotExist

def get_clean_html(node):
    if node.__class__.__name__ == 'HtmlElement':
        text = html.tostring(node, pretty_print=True)
        text = ' '.join(text.decode('utf-8').split())
    else:
        text = node
    cleaner = Cleaner(safe_attrs_only=True, add_nofollow=True)
    cleaned_html = cleaner.clean_html(text.strip())
    return re.sub(r'</p>$', '', re.sub(r'^<p>', '', cleaned_html))


def get_content(path, xpath_query=''):
    """
    Fetches the given URL, extracts, cleans, and returns the necessary data.
    """
    o = urlparse(path)
    if o.scheme in ['http', 'https']:
        r = requests.get(path)
        r.raise_for_status()
        text = r.text
    else:
        if not os.path.exists(path):
            raise FeedPathDoesNotExist
        with open(path) as f:
            text = f.read()
    if not xpath_query:
        return text
    tree = html.fromstring(text)
    elems = tree.xpath(xpath_query)
    if not elems:
        return ''
    return get_clean_html(elems[0])


def lazyattr(fn):
    """
    Lazy loaded attribute.
    http://stackoverflow.com/a/3013910
    """
    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazyattr(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)

    return _lazyattr


def render_template(node, context={}, loc=(__title__.lower(), 'templates')):
    env = Environment(loader=PackageLoader(loc[0], loc[1]))
    env.globals['get_content'] = get_content
    try:
        template = env.get_template(node)
    except TemplateNotFound:
        template = env.from_string(node)
    return template.render(context)
