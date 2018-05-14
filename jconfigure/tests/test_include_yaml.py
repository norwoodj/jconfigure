#!/usr/bin/env python
import unittest
from unittest.mock import patch

from ..utils import get_parser_for_file
from ..exceptions import TagConstructionException, UnsupportedNodeTypeException

from .test_utils import get_full_test_file_path


class TestIncludeYaml(unittest.TestCase):
    @staticmethod
    def parse_file(filename):
        parser = get_parser_for_file(filename)
        return parser.parse(filename)

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

        ans = TestIncludeYaml.parse_file(get_full_test_file_path("successful_include_files.yaml"))
        self.assertEqual(
            ans,
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
        ans = TestIncludeYaml.parse_file(get_full_test_file_path("chain.yaml"))
        self.assertEqual(ans, {
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
