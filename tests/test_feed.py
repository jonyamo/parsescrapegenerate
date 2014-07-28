# -*- coding: utf-8 -*-

"""
test_feed
---------

Tests for `parsescrapegenerate.feed` module.
"""
import sys
import time

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from parsescrapegenerate import config, feed
from parsescrapegenerate.exceptions import InvalidFeedFormat

TIMESTAMP=1404184359

class TestFeed(unittest.TestCase):
    def setUp(self):
        self.conf = config.get_config('tests/test-config/valid-config.yml')
        self.feed = feed.get_feed()
        self.feed.link = self.conf['path']

    def test_get_feed(self):
        """
        Test that given a valid format, a valid feed object is returned.
        """
        self.assertIsInstance(feed.get_feed('rss'), feed.RssFeed)
        self.assertIsInstance(feed.get_feed('atom'), feed.AtomFeed)

    def test_get_feed_invalid(self):
        """
        Test that given an invalid format, `exceptions.InvalidFeedFormat` is
        raised.
        """
        self.assertRaises(InvalidFeedFormat, feed.get_feed, 'foo')

    def test_fetch_title(self):
        """
        Test that the correct title is fetched.
        """
        self.assertEqual(self.feed.fetch_title(), "Sample HTML Page")

    def test_fetch_lang(self):
        """
        Test that the correct lang is fetched.
        """
        self.assertEqual(self.feed.fetch_lang(), "en-US")

    def test_fetch_entries(self):
        """
        Test that the correct number of entries are fetched.
        """
        entries = self.feed.fetch_entries(self.conf['entry'])
        self.assertEqual(len(entries), 3)

    def test_fetch_entry_vals(self):
        """
        Test that the correct entry vals are fetched.
        """
        entries = self.feed.fetch_entries(self.conf['entry'])
        self.assertEqual(entries[0].title, "Entry1 Title")
        self.assertEqual(entries[1].link, "http://example.com/entry2.html")
        self.assertEqual(entries[2].content, "Entry3 Content")


class TestAtomFeed(unittest.TestCase):
    def setUp(self):
        self.atom_feed = feed.get_feed('atom')

    def test_get_date(self):
        """
        Test that Atom feeds set the date format correctly.
        """
        self.assertEqual(self.atom_feed.get_date(time.gmtime(TIMESTAMP)),
                         '2014-07-01T03:12:39Z')


class TestRssFeed(unittest.TestCase):
    def setUp(self):
        self.rss_feed = feed.get_feed('rss')

    def test_get_date(self):
        """
        Test that RSS feeds set the date format correctly.
        """
        self.assertEqual(self.rss_feed.get_date(time.gmtime(TIMESTAMP)),
                         'Tue, 01 Jul 2014 03:12:39 Z')


class TestEntry(unittest.TestCase):
    def setUp(self):
        self.entry = feed.Entry()

    def test_generate_tag(self):
        """
        Test that tags are generated correctly.
        """
        date_format = '%a, %b %d %Y'
        self.entry.link = 'http://example.com/foo/bar/baz'
        self.entry.published = time.strftime(date_format, time.gmtime(TIMESTAMP))
        self.assertEqual(self.entry.generate_tag(date_format),
                         'tag:example.com,2014-07-01:/foo/bar/baz')

    def test_get_val_with_template(self):
        """
        Test that when a template is given, entry vals are correctly
        interpolated.
        """
        config = {'title':'foo-{{ entry.title }}-bar'}
        vals = {'title':'uncreative test title'}
        self.assertEqual(self.entry.get_val('title', config, vals),
                         'foo-uncreative test title-bar')

    def test_get_val_without_template(self):
        """
        Test that when no template is given, entry vals are correctly
        interpolated.
        """
        config = {}
        vals = {'title':'uncreative test title'}
        self.assertEqual(self.entry.get_val('title', config, vals),
                         'uncreative test title')


if __name__ == '__main__':
    unittest.main()
