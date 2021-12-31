#!/bin/bash

# These envars are required!

if [ -z "${token}" ]; then
    printf "You are required to provide a GitHub token.\n"
    exit 1
fi

# Ensure input token is defined
export GITHUB_TOKEN=${token}

if [ -z "${user}" ]; then
    printf "Please provide a user input for the username associated with the token.\n"
    exit 1
fi

if [ -z "${package}" ]; then
    printf "An input package or spec string is required to build.\n"
    exit 1
fi

# If deploy is set to true and we don't have a uri, this is an error 
if [ "${deploy}" == "true" ] && [ -z "${uri}" ]; then
    printf "If you want to deploy you must define a uri (unique resource identifier)\n"
    exit 1
fi

# Run paks for the specs provided, with deploy or not
if [ "${deploy}" == "true" ]; then
    paks build "${package}"
else
    paks build "${package}" --push "${uri}"
fi
