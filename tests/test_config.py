# -*- coding: utf-8 -*-

"""
test_config
-----------

Tests for `parsescrapegenerate.config` module.
"""
import sys

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from parsescrapegenerate import config
from parsescrapegenerate.exceptions import (
    ConfigDoesNotExist, ConfigIsNotValid, ConfigMissingRequiredKey
)

class TestConfig(unittest.TestCase):
    def test_get_config(self):
        """
        Test opening and reading config file.
        """
        conf = config.get_config('tests/test-config/valid-config.yml')
        expected_conf = {
            'title': "Sample Feed Config",
            'path': "tests/test-main/sample.html",
            'entry': {
                'templates': {
                    'link': "http://example.com{{ entry.link }}",
                },
                'xpath': {
                    'context': "//div[@class='entry']",
                    'title': "h2[@class='title']/a/text()",
                    'link': "h2[@class='title']/a/@href",
                    'content': "div[@class='content']/text()"
                }
            }
        }
        self.assertEqual(conf, expected_conf)

    def test_get_config_does_not_exist(self):
        """
        Test that `exceptions.ConfigDoesNotExist` is raised when attempting to
        get a non-existent config file.
        """
        self.assertRaises(
            ConfigDoesNotExist,
            config.get_config,
            'tests/test-config/this-does-not-exist.yml'
        )

    def test_invalid_config(self):
        """
        Test that `exceptions.ConfigIsNotValid` is raised when an invalid
        config file is given.
        """
        self.assertRaises(ConfigIsNotValid, config.get_config,
                          'tests/test-config/invalid-config.yml')

    def test_missing_required_key(self):
        """
        Test that `exceptions.ConfigMissingRequiredKey` is raised when the
        given config file is missing a required key.
        """
        self.assertRaises(ConfigMissingRequiredKey, config.get_config,
                          'tests/test-config/missing-key-config.yml')


if __name__ == '__main__':
    unittest.main()
