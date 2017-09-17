#!/usr/bin/env python

class FilesNotFoundException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class FileParsingException(Exception):
    def __init__(self, filename):
        super().__init__("Exception thrown while processing {}".format(filename))


class TagConstructionException(Exception):
    def __init__(self, tag_name, filename, message):
        super().__init__("Error constructing {tag} tag in file {filename}. {message}".format(
            tag=tag_name,
            filename=filename,
            message=message,
        ))


class UnsupportedNodeTypeException(Exception):
    def __init__(self, tag_parser_type, node_type):
        super().__init__("Yaml Tag Parser {} cannot parse nodes of type {}!".format(tag_parser_type, node_type))
