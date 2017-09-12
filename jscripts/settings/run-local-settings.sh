#!/usr/bin/env bash

source ${SCRIPT_DIR}/settings/common.sh
source ${SCRIPT_DIR}/utilities/docker-utilities.sh
source ${SCRIPT_DIR}/utilities/generate-certificate-utilities.sh

##
# Run Local Configuration
##
: ${DAEMON:="false"}


function print_run_local_applications_usage_list {
    print_app_usage_list
}

function get_applications_to_run_locally {
    get_app_list
}

function print_additional_options_usage_list {
    echo "  --daemon, -d                 Run the service as daemon"
}

function handle_additional_options {
    local option=${1}

    case ${option} in
        -d | --daemon) DAEMON="true" ;;
        -*)            return 1 ;;
    esac
}

function get_local_docker_compose_path_for_app {
    local app=${1}
    echo "docker/docker-compose-${app}.yaml"
}


##
# Hooks
##
function pre_run_local_hook {
    local app=${1}
    log_debug "Pre Run Local hook for application ${app}"
}

function post_run_local_hook {
    local app=${1}
    log_debug "Pre Run Local hook for application ${app}"
}
