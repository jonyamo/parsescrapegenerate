# -*- coding: utf-8 -*-

"""
test_utils
----------

Tests for `parsescrapegenerate.utils` module.
"""
import sys

if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest

from parsescrapegenerate import utils

class TestUtils(unittest.TestCase):
    def test_get_clean_html(self):
        self.assertEqual(utils.get_clean_html(' <p>foobar</p> '), 'foobar')

    def test_get_content(self):
        self.assertEqual(
            utils.get_content('tests/test-main/sample.html',
                              '//title/text()'), 'Sample HTML Page')

    def test_render_template_file(self):
        self.assertEqual(
            utils.render_template('template.txt', {'bar':'quux'},
                                  ('tests', 'test-utils')), 'fooquux')

    def test_render_template_string(self):
        self.assertEqual(
            utils.render_template('foo{{ bar }}', {'bar':'quux'}), 'fooquux')


if __name__ == '__main__':
    unittest.main()
