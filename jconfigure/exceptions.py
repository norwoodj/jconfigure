#!/usr/bin/env python


class FileParsingException(Exception):
    def __init__(self, filename):
        super().__init__("Exception thrown while processing {}".format(filename))


class FilesNotFoundException(Exception):
    def __init__(self, msg):
        super().__init__(msg)
