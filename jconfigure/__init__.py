#!/usr/bin/env python
import logging
import logging.config
import os

from .exceptions import FilesNotFoundException, FileParsingException
from .parsers import SUPPORTED_FILE_EXTENSIONS, CONFIG_FILENAME_FORMAT
from .utils import merge_configuration_from_dict_root, parse_file

_LOGGER = logging.getLogger(__name__)


def _get_configuration_dirs(configuration_dirs_arg):
    if configuration_dirs_arg is None:
        return (
            os.environ.get("JCONFIGURE_CONFIG_DIRECTORIES").split(",")
            if "JCONFIGURE_CONFIG_DIRECTORIES" in os.environ
            else [os.path.join(os.getcwd(), "config")]
        )

    elif type(configuration_dirs_arg) is basestring:
        return [configuration_dirs_arg]

    return configuration_dirs_arg


def _parse_file_handle_exceptions(filename, fail_on_parse_error):
    try:
        return parse_file(filename)
    except Exception as e:
        if fail_on_parse_error:
            _LOGGER.error("Exception thrown while parsing file {}!".format(filename))
            raise FileParsingException(filename) from e
        else:
            _LOGGER.warn("Exception thrown while parsing file {}. fail_on_parse_error is not set, continuing".format(
                filename
            ))

            return {}


def _merge_configuration_from_file(base_config, filename, fail_on_parse_error):
    overrides = _parse_file_handle_exceptions(filename, fail_on_parse_error)
    merge_configuration_from_dict_root(base_config, overrides)


def _find_available_config_files_in_directory(directory, basename):
    possible_config_files = (
        os.path.join(directory, CONFIG_FILENAME_FORMAT.format(basename=basename, extension=extension))
        for extension in SUPPORTED_FILE_EXTENSIONS
    )

    return [config_file for config_file in possible_config_files if os.path.isfile(config_file)]


def _handle_available_files_in_directories(
    base_config,
    file_basenames,
    configuration_dirs,
    fail_on_parse_error,
    fail_on_missing_files
):
    basename_found = {b: False for b in file_basenames}

    for basename in file_basenames:
        for directory in configuration_dirs:
            config_files_in_dir = _find_available_config_files_in_directory(directory, basename)

            if len(config_files_in_dir) == 0:
                _LOGGER.debug("No config files for basename {} found in directory {}".format(basename, directory))
            else:
                basename_found[basename] = True

            for f in config_files_in_dir:
                _LOGGER.debug("Parsing file {} and merging with config".format(f))
                _merge_configuration_from_file(
                    base_config=base_config,
                    filename=f,
                    fail_on_parse_error=fail_on_parse_error,
                )

    for basename, found in basename_found.items():
        if fail_on_missing_files and not found:
            _LOGGER.error("No files found for basename {} in any directory and fail_on_missing_files is set, exiting".format(basename))
            raise FilesNotFoundException("No files found for basename {} in any directory".format(basename))


def _handle_available_defaults_files(
    base_config,
    defaults_basename,
    configuration_dirs,
    fail_on_parse_error,
    fail_on_missing_files
):
    _LOGGER.debug("Searching for defaults config files...")
    _handle_available_files_in_directories(
        base_config=base_config,
        file_basenames=[defaults_basename],
        configuration_dirs=configuration_dirs,
        fail_on_parse_error=fail_on_parse_error,
        fail_on_missing_files=fail_on_missing_files,
    )


def _handle_active_profiles_files(
    base_config,
    active_profiles,
    configuration_dirs,
    fail_on_parse_error,
    fail_on_missing_files
):
    _LOGGER.debug("Searching for active profile config files...")
    _handle_available_files_in_directories(
        base_config=base_config,
        file_basenames=active_profiles,
        configuration_dirs=configuration_dirs,
        fail_on_parse_error=fail_on_parse_error,
        fail_on_missing_files=fail_on_missing_files,
    )


def _configure_logging(
    configuration_dirs,
    logging_config_filename,
    fail_on_parse_error,
    fail_on_missing_files
):
    logging_config = {}
    _handle_available_files_in_directories(
        base_config=logging_config,
        file_basenames=[logging_config_filename],
        configuration_dirs=configuration_dirs,
        fail_on_parse_error=fail_on_parse_error,
        fail_on_missing_files=fail_on_missing_files,
    )

    logging.config.dictConfig(logging_config)
    _LOGGER.debug("Configured logging")


def configure(
    configuration_dirs=None,
    logging_config_filename="logging",
    defaults_basename="defaults",
    active_profiles=None,
    fail_on_parse_error=True,
    fail_on_missing_files=False,
):
    """
    :param configuration_dirs: The directories from which configuration files will be pulled, either a single string, or
                               a list of strings. If None is passed, reads a comma seperated list of directories from
                               an environment variable JCONFIGURE_CONFIG_DIRECTORIES, if this variable is not set
                               defaults to a subdirectory of the current working directory called "config"
    :param logging_config_filename: If provided (not None), read config files matching this base name and any supported
                                    extension and use the read config to configure the _LOGGER
    :param defaults_basename: The name of the default config files that are read first, same as the profile, it is the
                              basename of the file to look for without an extension. Defaults to "defaults"
    :param active_profiles: The list of profiles currently active, if None is passed, this will be read from an
                            environment variable JCONFIGURE_ACTIVE_PROFILES. This variable should be a comma separated
                            list of strings. For each profile a file with the name {profile}.{extension} will be read,
                            where extension is one of the allowed file types
    :param fail_on_parse_error: If False suppress any exceptions thrown while processing a file. Defaults to True
    :param fail_on_missing_files: If True, raise an exception if an expected file is not found. Defaults to False

    :return: The configuration dictionary pulled from the configuration files specified under configuration_dir
    """
    configuration_dirs = _get_configuration_dirs(configuration_dirs)

    _configure_logging(
        configuration_dirs=configuration_dirs,
        logging_config_filename=logging_config_filename,
        fail_on_parse_error=fail_on_parse_error,
        fail_on_missing_files=fail_on_missing_files,
    )

    active_profiles = (
        active_profiles or
        os.environ.get("JCONFIGURE_ACTIVE_PROFILES").split(",") if "JCONFIGURE_ACTIVE_PROFILES" in os.environ else []
    )

    base_config = {}

    _LOGGER.info("Configuring Application using files in config directories [{}]".format(", ".join(configuration_dirs)))
    _LOGGER.info("Active profiles: [{}]".format(", ".join(active_profiles)))

    _handle_available_defaults_files(
        base_config=base_config,
        configuration_dirs=configuration_dirs,
        defaults_basename=defaults_basename,
        fail_on_parse_error=fail_on_parse_error,
        fail_on_missing_files=fail_on_missing_files,
    )

    _handle_active_profiles_files(
        base_config=base_config,
        configuration_dirs=configuration_dirs,
        active_profiles=active_profiles,
        fail_on_parse_error=fail_on_parse_error,
        fail_on_missing_files=fail_on_missing_files,
    )

    return base_config
