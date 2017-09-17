#!/usr/bin/env python
import os
import json

from yaml import YAMLObject, Loader, load
from yaml.nodes import ScalarNode, SequenceNode, MappingNode
from .exceptions import TagConstructionException, UnsupportedNodeTypeException


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
                filename=context["filename"],
            )

        return os.path.join(*file_paths)


class EnvVar(ArgListAcceptingYamlTag):
    yaml_tag = "!EnvVar"
    supported_node_types = (ScalarNode, MappingNode)

    @classmethod
    def map_node_data(cls, context, name, default=None):
        if name not in os.environ and default is None:
            cls.handle_tag_construction_error(
                message="Environment Variable '{}' not set, and no default provided!".format(name),
                filename=context["filename"],
            )

        return os.environ.get(name, default)


class RelativeFileIncludingYamlTag(ArgListAcceptingYamlTag):
    supported_node_types = (ScalarNode, MappingNode)

    @classmethod
    def handle_included_file(cls, context, file_handle):
        raise NotImplementedError()

    @classmethod
    def map_node_data(cls, context, filename):
        current_file_directory = os.path.dirname(context["filename"])
        full_file_path = os.path.join(current_file_directory, filename)

        try:
            with open(full_file_path) as file_handle:
                return cls.handle_included_file(context, file_handle)

        except IOError as e:
            cls.handle_tag_construction_error(
                message="Attempted to include relative file {}, which doesn't exist!".format(filename),
                filename=context["filename"],
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
                filename=context["filename"],
                exc=e,
            )


class IncludeYaml(RelativeFileIncludingYamlTag):
    yaml_tag = "!IncludeYaml"

    @classmethod
    def handle_included_file(cls, context, file_handle):
        try:
            context_passing_loader = lambda stream: ContextPassingYamlLoader(stream, {"filename": file_handle.name})
            return load(file_handle, Loader=context_passing_loader)
        except ValueError as e:
            cls.handle_tag_construction_error(
                message="Failed to parse relative yaml file {}!".format(file_handle.name),
                filename=context["filename"],
                exc=e,
            )


class IncludeText(RelativeFileIncludingYamlTag):
    yaml_tag = "!IncludeText"

    @classmethod
    def handle_included_file(cls, context, file_handle):
        return file_handle.read().strip()
