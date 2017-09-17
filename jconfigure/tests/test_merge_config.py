#!/usr/bin/env python

import unittest
from ..utils import merge_configuration_from_dict_root


class TestMergeConfiguration(unittest.TestCase):
    def test_merge_with_nothing(self):
        one = {"a": 1, "b": []}
        two = {}
        merge_configuration_from_dict_root(one, two)

        self.assertEqual({"a": 1, "b": []}, one)

        one = {"a": 1, "b": []}
        two = {}
        merge_configuration_from_dict_root(two, one)

        self.assertEqual({"a": 1, "b": []}, two)

    def test_merge_deep(self):
        one = {"a": 1, "b": {"c": 2}}
        two = {"b": {"c": 3}, "d": 4}
        merge_configuration_from_dict_root(one, two)

        self.assertEqual({"a": 1, "b": {"c": 3}, "d": 4}, one)

    def test_merge_overwrite_dict(self):
        one = {"a": 1, "b": {"c": 3}}
        two = {"b": 2}
        merge_configuration_from_dict_root(one, two)

        self.assertEqual({"a": 1, "b": 2}, one)

    def test_merge_overwrite_with_list(self):
        one = {"a": 1, "b": {"c": 3}}
        two = {"b": ["d"]}
        merge_configuration_from_dict_root(one, two)

        self.assertEqual({"a": 1, "b": ["d"]}, one)

    def test_merge_dont_overwrite_with_dict(self):
        one = {"a": 1, "b": {"c": 3}}
        two = {"b": {}, "a": 2}
        merge_configuration_from_dict_root(one, two)

        self.assertEqual({"a": 2, "b": {"c": 3}}, one)
