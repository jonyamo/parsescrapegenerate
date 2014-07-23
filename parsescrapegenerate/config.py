# -*- coding: utf-8 -*-

"""
parsescrapegenerate.config
----------------------

ParseScrapeGenerate configuration handling.
"""
import os
import yaml

from .exceptions import (
    ConfigDoesNotExist, ConfigIsNotValid, ConfigMissingRequiredKey
)

def get_config(config_path):
    """
    Parse given config_path and return dict.
    """
    if not os.path.exists(config_path):
        raise ConfigDoesNotExist

    with open(config_path) as f:
        try:
            config_dict = yaml.safe_load(f)
        except (yaml.scanner.ScannerError, yaml.parser.ParserError):
            raise ConfigIsNotValid(
                "{0} is not a valid YAML file".format(config_path))

    return _validate_config(config_dict)


def _validate_config(config_dict):
    """
    Validate given config dict.
    """
    errmsg = "Missing required key: {0}"

    if 'path' not in config_dict:
        raise ConfigMissingRequiredKey(errmsg.format('path'))
    if 'entry' not in config_dict:
        raise ConfigMissingRequiredKey(errmsg.format('entry'))
    if 'xpath' not in config_dict['entry']:
        raise ConfigMissingRequiredKey(errmsg.format('xpath'))
    if 'context' not in config_dict['entry']['xpath']:
        raise ConfigMissingRequiredKey(errmsg.format('context'))

    return config_dict

