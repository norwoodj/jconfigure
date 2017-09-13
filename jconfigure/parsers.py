#!/usr/bin/env python
import os
import json
from .exceptions import FileParsingException


class JsonConfigFileParser:
    FILE_EXTENSIONS = [".json"]

    @staticmethod
    def parse(filename):
        with open(filename) as json_file:
            return json.load(json_file)


__AVAILABLE_FILE_PARSERS = [
    JsonConfigFileParser,
]

__FILE_EXTENSION_TO_PARSERS = {
    extension: parser
    for parser in __AVAILABLE_FILE_PARSERS
    for extension in parser.FILE_EXTENSIONS
}

SUPPORTED_FILE_EXTENSIONS = list(__FILE_EXTENSION_TO_PARSERS.keys())


def parse_file(logger, filename, fail_on_parse_error=True):
    _, extension = os.path.splitext(filename)
    parser = __FILE_EXTENSION_TO_PARSERS[extension]

    try:
        return parser.parse(filename)
    except Exception as e:
        if fail_on_parse_error:
            logger.error("Exception thrown while parsing file {} using parser {}, exiting!".format(filename, parser))
            raise FileParsingException(filename) from e
        else:
            logger.warn("Exception thrown while parsing file {} using parser {}. fail_on_parse_error is not set, continuing".format(
                filename, parser
            ))

            return {}
