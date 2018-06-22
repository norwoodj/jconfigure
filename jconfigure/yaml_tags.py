#!/usr/bin/env python
import itertools
import json
import os

from yaml import YAMLObject, Loader, load
from yaml.constructor import BaseConstructor
from yaml.nodes import ScalarNode, SequenceNode, MappingNode

from .exceptions import TagConstructionException, UnsupportedNodeTypeException


# monkey patch construct_object to ensure alias expansion occurs before our custom yaml tags refer to any aliases
def construct_object_deep(self, node, deep=True):
    return construct_object_orig(self, node, deep)


construct_object_orig = BaseConstructor.construct_object
BaseConstructor.construct_object = construct_object_deep


class ContextPassingYamlLoader(Loader):
    def __init__(self, stream, context):
        super().__init__(stream)
        self.context = context


class ArgListAcceptingYamlTag(YAMLObject):
    supported_node_types = (ScalarNode, SequenceNode, MappingNode)

    @classmethod
    def __get_handler_for_node_type(cls, parsing_node_type):
        handler_map = {
            node_type: handler for node_type, handler in [
                (ScalarNode, cls.map_scalar_node),
                (SequenceNode, cls.map_sequence_node),
                (MappingNode, cls.map_mapping_node),
            ] if node_type in cls.supported_node_types
        }

        return handler_map.get(parsing_node_type)

    @classmethod
    def __get_exception(cls, message, filename):
        return TagConstructionException(
            tag_name=cls.yaml_tag,
            filename=filename,
            message=message,
        )

    @classmethod
    def map_scalar_node(cls, loader, node):
        loaded_node = loader.construct_scalar(node)
        return cls.map_node_data(loader.context, loaded_node)

    @classmethod
    def map_sequence_node(cls, loader, node):
        loaded_node = loader.construct_sequence(node, deep=True)
        return cls.map_node_data(loader.context, *loaded_node)

    @classmethod
    def map_mapping_node(cls, loader, node):
        loaded_node = loader.construct_mapping(node, deep=True)
        return cls.map_node_data(loader.context, **loaded_node)

    @classmethod
    def map_node_data(cls, context, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def handle_tag_construction_error(cls, message, filename, exc=None):
        if exc is not None:
            raise cls.__get_exception(message, filename) from exc
        else:
            raise cls.__get_exception(message, filename)

    @classmethod
    def from_yaml(cls, loader, node):
        handler = cls.__get_handler_for_node_type(type(node))

        if handler is None:
            raise UnsupportedNodeTypeException(cls, type(node))

        return handler(loader, node)


class JoinFilePaths(ArgListAcceptingYamlTag):
    yaml_tag = "!JoinFilePaths"
    supported_node_types = (SequenceNode, MappingNode)

    @classmethod
    def map_node_data(cls, context, *args, **kwargs):
        file_paths = kwargs.get("paths") or args

        if len(file_paths) == 0:
            cls.handle_tag_construction_error(
                message="No paths provided, provide them either with a 'paths' mapping, or a list of paths",
                filename=context["_parsing_filename"],
            )

        return os.path.join(*file_paths)


class ContextValue(ArgListAcceptingYamlTag):
    yaml_tag = "!ContextValue"
    supported_node_types = (ScalarNode, MappingNode)

    @classmethod
    def map_node_data(cls, context, key, default=None):
        if key not in context and default is None:
            cls.handle_tag_construction_error(
                message="Context Key '{}' not set, and no default provided!".format(key),
                filename=context["_parsing_filename"],
            )

        return context.get(key, default)


class EnvVar(ArgListAcceptingYamlTag):
    yaml_tag = "!EnvVar"
    supported_node_types = (ScalarNode, MappingNode)

    @classmethod
    def map_node_data(cls, context, name, default=None):
        if name not in os.environ and default is None:
            cls.handle_tag_construction_error(
                message="Environment Variable '{}' not set, and no default provided!".format(name),
                filename=context["_parsing_filename"],
            )

        return os.environ.get(name, default)


class StringFormat(ArgListAcceptingYamlTag):
    yaml_tag = "!StringFormat"
    supported_node_types = (SequenceNode, MappingNode)

    @classmethod
    def map_node_data(cls, context, *args, **kwargs):
        if "string" not in kwargs and len(args) < 1:
            cls.handle_tag_construction_error(
                message="Either a list of at least 1 string, or a dictionary containing keys 'string' and 'format_args' must be provided",
                filename=context["_parsing_filename"],
            )

        string = kwargs.get("string") or args[0]

        if type(string) is not str:
            string_arg_type = "'string' keyword argument" if "string" in kwargs else "First list argument"
            cls.handle_tag_construction_error(
                message="{string_arg_type} must be a string!".format(string_arg_type=string_arg_type),
                filename=context["_parsing_filename"],
            )

        if "format_args" not in kwargs and len(args) < 2:
            return string

        format_args = kwargs.get("format_args") or args[1]

        if type(format_args) not in (dict, list):
            format_arg_type = "'format_args' keyword argument" if "format_args" in kwargs else  "Second list argument"
            cls.handle_tag_construction_error(
                message="{format_arg_type} must be a dictionary or a list!".format(format_arg_type=format_arg_type),
                filename=context["_parsing_filename"],
            )

        return string.format(**format_args) if type(format_args) is dict else string.format(*format_args)


class Chain(ArgListAcceptingYamlTag):
    yaml_tag = "!Chain"
    supported_node_types = (SequenceNode, MappingNode)

    @classmethod
    def map_node_data(cls, context, *args, **kwargs):
        lists = kwargs.get("lists") or args
        for l in lists:
            if type(l) is not list:
                cls.handle_tag_construction_error(
                    message="All elements of !Chain node must be lists",
                    filename=context["_parsing_filename"],
                )

        return list(itertools.chain.from_iterable(lists))


class RelativeFileIncludingYamlTag(ArgListAcceptingYamlTag):
    supported_node_types = (ScalarNode, MappingNode)

    @classmethod
    def handle_included_file(cls, context, file_handle):
        raise NotImplementedError()

    @classmethod
    def map_node_data(cls, context, filename):
        current_file_directory = os.path.dirname(context["_parsing_filename"])
        full_file_path = os.path.join(current_file_directory, filename)

        try:
            with open(full_file_path) as file_handle:
                return cls.handle_included_file(context, file_handle)

        except IOError as e:
            cls.handle_tag_construction_error(
                message="Attempted to include relative file {}, which doesn't exist!".format(filename),
                filename=context["_parsing_filename"],
                exc=e,
            )


class IncludeJson(RelativeFileIncludingYamlTag):
    yaml_tag = "!IncludeJson"

    @classmethod
    def handle_included_file(cls, context, file_handle):
        try:
            return json.load(file_handle)
        except ValueError as e:

            cls.handle_tag_construction_error(
                message="Failed to parse relative json file {}!".format(file_handle.name),
                filename=context["_parsing_filename"],
                exc=e,
            )


class IncludeYaml(RelativeFileIncludingYamlTag):
    yaml_tag = "!IncludeYaml"

    @classmethod
    def handle_included_file(cls, context, file_handle):
        try:
            full_context = {**context, "_parsing_filename": file_handle.name}
            context_passing_loader = lambda stream: ContextPassingYamlLoader(stream, full_context)
            return load(file_handle, Loader=context_passing_loader)
        except ValueError as e:
            cls.handle_tag_construction_error(
                message="Failed to parse relative yaml file {}!".format(file_handle.name),
                filename=context["_parsing_filename"],
                exc=e,
            )


class IncludeText(RelativeFileIncludingYamlTag):
    yaml_tag = "!IncludeText"

    @classmethod
    def handle_included_file(cls, context, file_handle):
        return file_handle.read().strip()
