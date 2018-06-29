#!/usr/bin/env python
import json
import unittest
import yaml

from unittest.mock import patch
from ..utils import get_parser_for_file
from ..exceptions import TagConstructionException, UnsupportedNodeTypeException
from .test_utils import get_full_test_file_path


class TestIncludeYaml(unittest.TestCase):
    @staticmethod
    def parse_file(filename, context={}):
        parser = get_parser_for_file(filename)
        return parser.parse(filename, context)

    def test_parse_working_yaml(self):
        self.assertEqual(
            TestIncludeYaml.parse_file(get_full_test_file_path("working_yaml.yaml")),
            {"a": 1, "b": {"c": 3}, "d": [4]},
        )

    @patch.dict("jconfigure.yaml_tags.os.environ", {"_TEST_ENV_VAR": "environment"})
    def test_env_var_tag(self):
        self.assertEqual(
            TestIncludeYaml.parse_file(get_full_test_file_path("successful_env_var.yaml")),
            {
                "env_var_scalar": "environment",
                "env_var_mapping": "environment",
                "env_var_default": "default_environment",
            }
        )

    def test_missing_env_var_tag(self):
        self.assertRaises(
            TagConstructionException,
            TestIncludeYaml.parse_file,
            get_full_test_file_path("missing_env_var.yaml"),
        )

    def test_env_var_unsupported_node(self):
        self.assertRaises(
            UnsupportedNodeTypeException,
            TestIncludeYaml.parse_file,
            get_full_test_file_path("unsupported_env_var.yaml"),
        )

    @patch.dict("jconfigure.yaml_tags.os.environ", {"_TEST_INCLUDE_DIR": "includes"})
    def test_include_files_successful(self):
        expected_include = {
            "jingles": "cat",
            "oscar": ["dog", "sleepy"],
        }

        actual = TestIncludeYaml.parse_file(get_full_test_file_path("successful_include_files.yaml"))
        self.assertEqual(
            actual,
            {
                "include_json_scalar": expected_include,
                "include_json_mapping": expected_include,
                "include_yaml_scalar": expected_include,
                "include_yaml_mapping": expected_include,
                "include_text_scalar": "animals",
                "include_text_mapping": "animals",
            }
        )

    def test_include_files_unsuccessful(self):
        self.assertRaises(
            TagConstructionException,
            TestIncludeYaml.parse_file,
            get_full_test_file_path("unsuccessful_include_files.yaml"),
        )

    def test_include_files_unsupported(self):
        self.assertRaises(
            UnsupportedNodeTypeException,
            TestIncludeYaml.parse_file,
            get_full_test_file_path("unsupported_include_files.yaml"),
        )

    def test_join_file_paths_unsupported(self):
        self.assertRaises(
            UnsupportedNodeTypeException,
            TestIncludeYaml.parse_file,
            get_full_test_file_path("unsupported_join_file_paths.yaml"),
        )

    def test_chain(self):
        actual = TestIncludeYaml.parse_file(get_full_test_file_path("chain.yaml"))
        self.assertEqual(actual, {
            "chain_sequence": [1, 2, 3, 4],
            "chain_mapping": [1, 2, 3, 4],
            "chain_mappings": [{"one": 1}, {"two": 2}, {"three": 3}, {"four": 4}],
        })

    def test_chain_not_list(self):
        self.assertRaises(
            TagConstructionException,
            TestIncludeYaml.parse_file,
            get_full_test_file_path("chain_not_list.yaml"),
        )

    def test_sub_include_successful(self):
        actual = TestIncludeYaml.parse_file(get_full_test_file_path("successful_multi_level_include_files.yaml"))
        self.assertEqual(actual, {
            "pets": [
                {"cat": "echo"},
                {"dog": "oscar"},
             ],
        })

    def test_sub_include_missing(self):
        self.assertRaises(
            TagConstructionException,
            TestIncludeYaml.parse_file,
            get_full_test_file_path("unsuccessful_multi_level_include_files.yaml"),
        )

    def test_context_successful(self):
        actual = TestIncludeYaml.parse_file(get_full_test_file_path("context_successful.yaml"), {"cat": "echo"})
        self.assertEqual(actual, {
            "pets": [
                {"cat_scalar": "echo"},
                {"cat_mapping": "echo"},
                {"dog": "oscar"},
            ],
        })

    def test_context_include(self):
        actual = TestIncludeYaml.parse_file(get_full_test_file_path("context_include.yaml"), {"cat": "echo"})
        self.assertEqual(actual, {
            "pets": {
                "cat": "echo",
                "dog": "oscar",
            },
        })

    def test_context_missing(self):
        self.assertRaises(
            TagConstructionException,
            TestIncludeYaml.parse_file,
            get_full_test_file_path("context_missing.yaml"),
            {"cat": "echo"},
        )

    def __check_string_format_output(self, actual):
        self.assertEqual(actual, {
            "string_sequence_none": "echo is a cat",
            "string_sequence_single": "echo is a cat",
            "string_sequence_multi": "echo is a cat and oscar is a dog",
            "string_sequence_extra": "echo is a cat and oscar is a dog",
            "string_mapping_none": "echo is a cat",
            "string_mapping_single": "echo is a cat",
            "string_mapping_multi": "echo is a cat and oscar is a dog",
            "string_mapping_extra": "echo is a cat and oscar is a dog",
        })

    def test_string_format_fails_scalar(self):
        self.assertRaises(
            UnsupportedNodeTypeException,
            TestIncludeYaml.parse_file,
            get_full_test_file_path("unsuccessful_string_format_scalar.yaml"),
        )

    def test_string_format_list_format_args(self):
        actual = TestIncludeYaml.parse_file(get_full_test_file_path("successful_string_format_list_format_args.yaml"))
        self.__check_string_format_output(actual)

    def test_string_format_mapping_format_args(self):
        actual = TestIncludeYaml.parse_file(get_full_test_file_path("successful_string_format_mapping_format_args.yaml"))
        self.__check_string_format_output(actual)

    def test_string_format_fails_non_string_sequence(self):
        self.assertRaises(
            TagConstructionException,
            TestIncludeYaml.parse_file,
            get_full_test_file_path("unsuccessful_string_format_non_string_sequence.yaml"),
        )

        try:
            TestIncludeYaml.parse_file(get_full_test_file_path("unsuccessful_string_format_non_string_sequence.yaml"))
        except TagConstructionException as e:
            self.assertEqual(e.reason, "First list argument must be a string!")

    def test_string_format_fails_non_string_mapping(self):
        self.assertRaises(
            TagConstructionException,
            TestIncludeYaml.parse_file,
            get_full_test_file_path("unsuccessful_string_format_non_string_mapping.yaml"),
        )

        try:
            TestIncludeYaml.parse_file(get_full_test_file_path("unsuccessful_string_format_non_string_mapping.yaml"))
        except TagConstructionException as e:
            self.assertEqual(e.reason, "'string' keyword argument must be a string!")

    def test_string_format_fails_mapping_no_string_key(self):
        self.assertRaises(
            TagConstructionException,
            TestIncludeYaml.parse_file,
            get_full_test_file_path("unsuccessful_string_format_mapping_no_string_key.yaml"),
        )

        try:
            TestIncludeYaml.parse_file(get_full_test_file_path("unsuccessful_string_format_mapping_no_string_key.yaml"))
        except TagConstructionException as e:
            self.assertEqual(
                e.reason,
                "Either a list of at least 1 string, or a dictionary containing keys 'string' and 'format_args' must be provided",
            )

    def test_string_format_fails_empty_list(self):
        self.assertRaises(
            TagConstructionException,
            TestIncludeYaml.parse_file,
            get_full_test_file_path("unsuccessful_string_format_empty_list.yaml"),
        )

        try:
            TestIncludeYaml.parse_file(get_full_test_file_path("unsuccessful_string_format_empty_list.yaml"))
        except TagConstructionException as e:
            self.assertEqual(
                e.reason,
                "Either a list of at least 1 string, or a dictionary containing keys 'string' and 'format_args' must be provided",
            )

    def test_string_format_fails_bad_second_arg_sequence(self):
        self.assertRaises(
            TagConstructionException,
            TestIncludeYaml.parse_file,
            get_full_test_file_path("unsuccessful_string_format_bad_second_arg_sequence.yaml"),
        )

        try:
            TestIncludeYaml.parse_file(get_full_test_file_path("unsuccessful_string_format_bad_second_arg_sequence.yaml"))
        except TagConstructionException as e:
            self.assertEqual(
                e.reason,
                "Second list argument must be a dictionary or a list!",
            )

    def test_string_format_fails_bad_second_arg_mapping(self):
        self.assertRaises(
            TagConstructionException,
            TestIncludeYaml.parse_file,
            get_full_test_file_path("unsuccessful_string_format_bad_second_arg_mapping.yaml"),
        )

        try:
            TestIncludeYaml.parse_file(get_full_test_file_path("unsuccessful_string_format_bad_second_arg_mapping.yaml"))
        except TagConstructionException as e:
            self.assertEqual(
                e.reason,
                "'format_args' keyword argument must be a dictionary or a list!",
            )

    def test_yaml_and_json_string(self):
        actual = TestIncludeYaml.parse_file(get_full_test_file_path("yaml_and_json_string.yaml"))
        self.assertEqual(json.loads(actual["string_json"]), {"pets": {"oscar": "dog", "echo": "cat"}})
        self.assertEqual(yaml.load(actual["string_yaml"]), {"pets": {"oscar": "dog", "echo": "cat"}})
