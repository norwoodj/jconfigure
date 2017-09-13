#!/usr/bin/env python
import json
import logging
import os
import yaml

from .exceptions import FileParsingException
from .yaml_tags import *

__LOGGER = logging.getLogger(__name__)


class JsonConfigFileParser:
    FILE_EXTENSIONS = [".json"]

    @staticmethod
    def parse(filename):
        with open(filename) as json_file:
            return json.load(json_file)


class YamlConfigFileParser:
    FILE_EXTENSIONS = [".yaml", ".yml"]

    @staticmethod
    def parse(filename):
        with open(filename) as yaml_file:
            context_passing_loader = lambda stream: ContextPassingYamlLoader(stream, {"filename": filename})
            return yaml.load(yaml_file, Loader=context_passing_loader)


__AVAILABLE_FILE_PARSERS = [
    JsonConfigFileParser,
    YamlConfigFileParser,
]

__FILE_EXTENSION_TO_PARSERS = {
    extension: parser
    for parser in __AVAILABLE_FILE_PARSERS
    for extension in parser.FILE_EXTENSIONS
}

SUPPORTED_FILE_EXTENSIONS = list(__FILE_EXTENSION_TO_PARSERS.keys())


def parse_file(filename, fail_on_parse_error=True):
    _, extension = os.path.splitext(filename)
    parser = __FILE_EXTENSION_TO_PARSERS[extension]

    try:
        return parser.parse(filename)
    except Exception as e:
        if fail_on_parse_error:
            __LOGGER.error("Exception thrown while parsing file {} using parser {}!".format(filename, parser))
            raise FileParsingException(filename) from e
        else:
            __LOGGER.warn("Exception thrown while parsing file {} using parser {}. fail_on_parse_error is not set, continuing".format(
                filename, parser
            ))

            return {}
