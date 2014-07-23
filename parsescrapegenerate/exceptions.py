# -*- coding: utf-8 -*-

"""
parsescrapegenerate.exceptions
--------------------------

All exceptions used in the ParseScrapeGenerate code base are defined here.
"""

class ParseScrapeGenerateException(Exception):
    """
    Base exception class. All ParseScrapeGenerate-specific exceptions should
    subclass this class.
    """


class ConfigDoesNotExist(ParseScrapeGenerateException):
    """
    Raised when given config_path does not exist.
    """


class ConfigIsNotValid(ParseScrapeGenerateException):
    """
    Raised when given config_path is not valid.
    """


class ConfigMissingRequiredKey(ParseScrapeGenerateException):
    """
    Raised when given config_path is missing a required key.
    """


class FeedPathDoesNotExist(ParseScrapeGenerateException):
    """
    Raised when given feed_path does not exist.
    """


class InvalidFeedFormat(ParseScrapeGenerateException):
    """
    Raised when given feed format is not valid.
    """

