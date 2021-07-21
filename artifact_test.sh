#!/usr/bin/env bash

set -euo pipefail

echo "--- :aws: Initial identity in command"
aws sts get-caller-identity

echo "--- Write a file to be uploaded"
echo "THIS IS A TEST" > test.txt

if [ "${DROP_ASSUMED_ROLE}" == "true" ]; then
    echo "--- :gear: Dropping assumed role"
    unset AWS_ACCESS_KEY_ID
    unset AWS_SECRET_ACCESS_KEY
    unset AWS_SESSION_TOKEN

    echo "--- :aws: Identity after dropping assumed role"
    aws sts get-caller-identity
else
    echo "--- NOT dropping assumed role!"
fi

if [ "${UPLOAD_FILE_IN_COMMAND}" == "true" ]; then
    echo "--- :aws: Identity before upload in command"
    aws sts get-caller-identity

    echo "--- :buildkite: Uploading manifest"
    buildkite-agent artifact upload test.txt
else
    echo "--- NOT uploading file in command!"
fi
