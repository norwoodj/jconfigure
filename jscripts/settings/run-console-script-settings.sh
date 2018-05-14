#!/usr/bin/env bash

[[ -n "${_RUN_CONSOLE_SCRIPT_SETTINGS_SH:+_}" ]] && return || readonly _SETUP_STUPIDCHESS_GAME_SETTINGS_SH=1

source ${SCRIPT_DIR}/utilities/command-line-utilities.sh
source ${SCRIPT_DIR}/utilities/docker-utilities.sh


function get_console_script_names {
    echo "tests"
}

function print_console_script_usage_list {
    bulleted_list <(get_console_script_names)
}

function get_images_necessary_to_run_script {
    local console_script=${1}
    echo "${TESTS_IMAGE}"
}

function get_docker_compose_path_for_script {
    local console_script=${1}
    echo "docker-compose.yaml"
}

function get_docker_compose_service_for_script {
    local console_script=${1}
    echo "tests"
}

function get_full_script_path {
    local console_script=${1}
    echo ""
}


##
# Hooks
##

function pre_run_console_script_hook {
    local console_script=${1}
    log_debug "Pre Run Console Script Hook for script ${console_script}"
}

function post_run_console_script_hook {
    local console_script=${1}
    log_debug "Post Run Console Script Hook for script ${console_script}"
}
