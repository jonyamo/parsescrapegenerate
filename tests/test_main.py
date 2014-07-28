# -*- coding: utf-8 -*-

"""
test_main
---------

Tests for `parsescrapegenerate.main` module.
"""
import sys

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from feedparser import FeedParserDict
from parsescrapegenerate import config, feed, main

class TestMain(unittest.TestCase):
    def test_parse(self):
        """
        Test that `main.parse` returns `feedparse.FeedParserDict`.
        """
        self.assertIsInstance(
            main.parse('tests/test-main/rss.xml'), FeedParserDict)

    def test_scrape(self):
        """
        Test that `main.scrape` returns a valid feed object.
        """
        conf = config.get_config('tests/test-config/valid-config.yml')
        self.assertIsInstance(main.scrape(conf), feed.RssFeed)

    def test_generate(self):
        pass


if __name__ == '__main__':
    unittest.main()
