import os
import json

from yaml import YAMLObject, Loader, load
from yaml.nodes import ScalarNode, SequenceNode, MappingNode
from .exceptions import FileParsingException


class ContextPassingYamlLoader(Loader):
    def __init__(self, stream, context):
        super().__init__(stream)
        self.context = context


class ArgListAcceptingYamlTag(YAMLObject):
    @classmethod
    def __get_exception(cls, message):
        return FileParsingException("Error constructing {tag} tag. {message}".format(
            tag=cls.yaml_tag,
            message=message,
        ))

    @classmethod
    def handle_tag_construction_error(cls, message, exc=None):
        if exc is not None:
            raise cls.__get_exception(message) from exc
        else:
            raise cls.__get_exception(message)

    @classmethod
    def map_node_data(cls, context, *args, **kwargs):
        raise NotImplementedError()

    @classmethod
    def from_yaml(cls, loader, node):
        if type(node) is ScalarNode:
            loaded_node = loader.construct_scalar(node)
            return cls.map_node_data(loader.context, loaded_node)
        if type(node) is SequenceNode:
            loaded_node = loader.construct_sequence(node, deep=True)
            return cls.map_node_data(loader.context, *loaded_node)
        if type(node) is MappingNode:
            loaded_node = loader.construct_mapping(node, deep=True)
            return cls.map_node_data(loader.context, **loaded_node)


class EnvVar(ArgListAcceptingYamlTag):
    yaml_tag = "!EnvVar"

    @classmethod
    def map_node_data(cls, context, name):
        if name not in os.environ:
            cls.handle_tag_construction_error("Environment Variable '{}' not set!".format(name))

        return os.environ[name]


class RelativeFileIncludingYamlTag(ArgListAcceptingYamlTag):
    @classmethod
    def handle_included_file(cls, file_handle):
        raise NotImplementedError()

    @classmethod
    def map_node_data(cls, context, filename):
        current_file_directory = os.path.dirname(context["filename"])
        full_file_path = os.path.join(current_file_directory, filename)
        try:
            with open(full_file_path) as file_handle:
                return cls.handle_included_file(file_handle)

        except IOError as e:
            cls.handle_tag_construction_error(
                "Attempted to include relative file {}, which doesn't exist!".format(filename),
                e,
            )


class IncludeJson(RelativeFileIncludingYamlTag):
    yaml_tag = "!IncludeJson"

    @classmethod
    def handle_included_file(cls, file_handle):
        try:
            return json.load(file_handle)
        except ValueError as e:
            cls.handle_tag_construction_error("Failed to parse relative json file {}!".format(filename), e)


class IncludeYaml(RelativeFileIncludingYamlTag):
    yaml_tag = "!IncludeYaml"

    @classmethod
    def handle_included_file(cls, file_handle):
        try:
            context_passing_loader = lambda stream: ContextPassingYamlLoader(stream, {"filename": file_handle.name})
            return load(file_handle, Loader=context_passing_loader)
        except ValueError as e:
            cls.handle_tag_construction_error("Failed to parse relative yaml file {}!".format(filename), e)


class IncludeText(RelativeFileIncludingYamlTag):
    yaml_tag = "!IncludeText"

    @classmethod
    def handle_included_file(cls, file_handle):
        return file_handle.read().strip()
