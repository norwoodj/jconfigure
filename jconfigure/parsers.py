#!/usr/bin/env python
import json
import logging
import os
import yaml

from .yaml_tags import *

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


def parse_file(filename):
    _, extension = os.path.splitext(filename)
    parser = __FILE_EXTENSION_TO_PARSERS[extension]
    return parser.parse(filename)
