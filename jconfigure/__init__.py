#!/usr/bin/env python
import logging
import os

from .parsers import SUPPORTED_FILE_EXTENSIONS, parse_file
from .exceptions import FilesNotFoundException

__CONFIG_FILENAME_FORMAT = "{basename}{extension}"


def __get_configuration_dirs(configuration_dirs_arg):
    if configuration_dirs_arg is None:
        return [os.path.join(os.getcwd(), "config")]

    elif type(configuration_dirs_arg) is basestring:
        return [configuration_dirs_arg]

    return configuration_dirs_arg


def __merge_configuration_from_file(logger, base_config, filename, fail_on_parse_error):
    base_config[filename] = parse_file(
        logger=logger,
        filename=filename,
        fail_on_parse_error=fail_on_parse_error,
    )


def __find_available_config_files_in_directory(directory, basename):
    possible_config_files = (
        os.path.join(directory, __CONFIG_FILENAME_FORMAT.format(basename=basename, extension=extension))
        for extension in SUPPORTED_FILE_EXTENSIONS
    )

    return [config_file for config_file in possible_config_files if os.path.isfile(config_file)]


def __handle_available_files_in_directories(
    logger,
    base_config,
    file_basenames,
    configuration_dirs,
    fail_on_parse_error,
    fail_on_missing_files
):
    basename_found = {b: False for b in file_basenames}

    for directory in configuration_dirs:
        for basename in file_basenames:
            config_files_in_dir = __find_available_config_files_in_directory(directory, basename)

            if len(config_files_in_dir) == 0:
                logger.info("No config files for basename {} found in directory {}".format(basename, directory))
            else:
                basename_found[basename] = True

            for f in config_files_in_dir:
                logger.info("Parsing file {} and merging with config".format(f))
                __merge_configuration_from_file(
                    logger=logger,
                    base_config=base_config,
                    filename=f,
                    fail_on_parse_error=fail_on_parse_error,
                )

    for basename, found in basename_found.items():
        if fail_on_missing_files and not found:
            logger.error("No files found for basename {} in any directory and fail_on_missing_files is set, exiting".format(basename))
            raise FilesNotFoundException("No files found for basename {} in any directory".format(basename))


def __handle_available_defaults_files(
    logger,
    base_config,
    defaults_basename,
    configuration_dirs,
    fail_on_parse_error,
    fail_on_missing_files
):
    logger.info("Searching for defaults files...")

    __handle_available_files_in_directories(
        logger=logger,
        base_config=base_config,
        file_basenames=[defaults_basename],
        configuration_dirs=configuration_dirs,
        fail_on_parse_error=fail_on_parse_error,
        fail_on_missing_files=fail_on_missing_files,
    )


def __handle_active_profiles_files(
    logger,
    base_config,
    active_profiles,
    configuration_dirs,
    fail_on_parse_error,
    fail_on_missing_files
):
    logger.info("Searching for active profile files...")

    __handle_available_files_in_directories(
        logger=logger,
        base_config=base_config,
        file_basenames=active_profiles,
        configuration_dirs=configuration_dirs,
        fail_on_parse_error=fail_on_parse_error,
        fail_on_missing_files=fail_on_missing_files,
    )


def configure(
    configuration_dirs=None,
    defaults_basename="defaults",
    active_profiles=None,
    fail_on_parse_error=True,
    fail_on_missing_files=False
):
    """
    :param configuration_dirs: The directories from which configuration files will be pulled, either a single string, or
                               a list of strings. If None is passed, defaults to a subdirectory of the cwd called
                               "config"
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
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    configuration_dirs = __get_configuration_dirs(configuration_dirs)
    active_profiles = active_profiles or os.environ.get("JCONFIGURE_ACTIVE_PROFILES", "").split(",")
    base_config = {}

    logger.info("Configuring Application using files in config directories [{}]".format(", ".join(configuration_dirs)))
    logger.info("Active profiles: [{}]".format(", ".join(active_profiles)))

    __handle_available_defaults_files(
        logger=logger,
        base_config=base_config,
        configuration_dirs=configuration_dirs,
        defaults_basename=defaults_basename,
        fail_on_parse_error=fail_on_parse_error,
        fail_on_missing_files=fail_on_missing_files,
    )

    __handle_active_profiles_files(
        logger=logger,
        base_config=base_config,
        configuration_dirs=configuration_dirs,
        active_profiles=active_profiles,
        fail_on_parse_error=fail_on_parse_error,
        fail_on_missing_files=fail_on_missing_files,
    )

    return base_config
