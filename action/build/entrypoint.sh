#!/bin/bash

# These envars are required!

if [ -z "${INPUT_TOKEN}" ]; then
    printf "You are required to provide a GitHub token.\n"
    exit 1
fi

if [ -z "${INPUT_USER}" ]; then
    printf "Please provide a user input for the username associated with the token.\n"
    exit 1
fi

if [ -z "${INPUT_PACKAGE}" ]; then
    printf "An input package or spec string is required to build.\n"
    exit 1
fi

# If deploy is set to true and we don't have a uri, this is an error 
if [ "${INPUT_DEPLOY}" == "true" ] && [ -z "${INPUT_URI}" ]; then
    printf "If you want to deploy you must define a uri (unique resource identifier)\n"
    exit 1
fi
# Repository name
repository_name=$(basename ${PWD})
printf "Repository name is ${repository_name}\n"

# Run paks for the specs provided, with deploy or not
if [ "${INPUT_DEPLOY}" == "true" ]; then
    paks build "${INPUT_PACKAGE}"
else
    paks build "${INPUT_PACKAGE}" --push "${INPUT_URI}"
fi
