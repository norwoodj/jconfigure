#!/usr/bin/env bash

[[ -n "${_APPLICATION_SETTINGS_SH:+_}" ]] && return || readonly _APPLICATION_SETTINGS_SH=1

##
# This is where you should define the names of every application that is built by this project, an application being some
# collection of docker containers that should run as an atomic unit. These names will be used in scripts throughout this
# project, for instance in the "run-locally.sh" script, where you will specify one of these applications to be run
##
readonly WEB_APPLICATION_NAME="jscripts-web"

readonly _APPLICATION_CONFIG=$(cat <<EOF
{
    "applications": [
        "${WEB_APPLICATION_NAME}"
    ],
    "imagesToRunApp": {
        "${WEB_APPLICATION_NAME}": ["${NGINX_IMAGE}"]
    }
}
EOF
)


function get_app_list {
    jq -r ".applications[]" <<< "${_APPLICATION_CONFIG}"
}

function print_app_usage_list {
    echo "  ${WEB_APPLICATION_NAME}  A web application"
}

function get_images_necessary_to_run_app {
    local app=${1}
    jq -r ".imagesToRunApp.${app}[]" <<< "${_APPLICATION_CONFIG}"
}

function get_current_application_version {
    grep "version=" setup.py | sed -E 's|version="(.*)",|\1|'
}
