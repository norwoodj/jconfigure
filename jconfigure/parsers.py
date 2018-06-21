#!/usr/bin/env python
import json
import os
import yaml

from .yaml_tags import *


class JsonConfigFileParser:
    FILE_EXTENSIONS = [".json"]

    @staticmethod
    def parse(filename, _):
        with open(filename) as json_file:
            return json.load(json_file)


class YamlConfigFileParser:
    FILE_EXTENSIONS = [".yaml", ".yml"]

    @staticmethod
    def parse(filename, context):
        with open(filename) as yaml_file:
            return yaml.load(
                yaml_file,
                Loader=lambda stream: ContextPassingYamlLoader(stream, {**context, "_parsing_filename": filename}),
            )


AVAILABLE_FILE_PARSERS = [
    JsonConfigFileParser,
    YamlConfigFileParser,
]

FILE_EXTENSION_TO_PARSERS = {
    extension: parser
    for parser in AVAILABLE_FILE_PARSERS
    for extension in parser.FILE_EXTENSIONS
}

SUPPORTED_FILE_EXTENSIONS = list(FILE_EXTENSION_TO_PARSERS.keys())
CONFIG_FILENAME_FORMAT = "{basename}{extension}"
