#!/usr/bin/env python
import os
from .exceptions import FileParsingException, FilesNotFoundException
from .parsers import FILE_EXTENSION_TO_PARSERS


def merge_configuration_from_dict_root(base_config, overrides):
    for k, v in overrides.items():
        if type(v) is dict and type(base_config.get(k)) is dict:
            merge_configuration_from_dict_root(base_config[k], v)
        else:
            base_config[k] = v

def get_parser_for_file(filename):
    _, extension = os.path.splitext(filename)
    return FILE_EXTENSION_TO_PARSERS[extension]

def parse_file(filename):
    if not os.path.isfile(filename):
        raise FilesNotFoundException(f"File {filename} doesn't exist!")

    parser = get_parser_for_file(filename)

    try:
        return parser.parse(filename)
    except Exception as e:
        raise FileParsingException(filename) from e
