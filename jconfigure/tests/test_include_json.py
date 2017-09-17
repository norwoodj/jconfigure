#!/usr/bin/env python
import unittest

from ..exceptions import FileParsingException, FilesNotFoundException
from ..utils import parse_file
from .test_utils import get_full_test_file_path


class TestIncludeJson(unittest.TestCase):
    def test_parse_working_json(self):
        self.assertEqual(
            parse_file(get_full_test_file_path("working_json.json")),
            {"a": 1, "b": {"c": 3}, "d": [4]},
        )

    def test_parse_failing_json(self):
        self.assertRaises(
            FileParsingException,
            parse_file,
            get_full_test_file_path("failing_json.json"),
        )

    def test_parse_nonexistant_file(self):
        self.assertRaises(
            FilesNotFoundException,
            parse_file,
            get_full_test_file_path("nonexistant_json.json"),
        )
