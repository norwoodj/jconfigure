#!/usr/bin/env python
import inspect
import os

_TEST_FILE_DIR = "test_files"


def get_full_test_file_path(filename):
    return os.path.join(os.path.dirname(inspect.stack()[1][1]), _TEST_FILE_DIR, filename)
