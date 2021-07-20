#!/usr/bin/env bash

set -euo pipefail

dropping_steps=(
    with-drop
    drop-with-env
    artifact-plugin-with-drop
    native-with-drop
)

uploading_steps=(
    no-drop
    native-no-drop
    with-drop
    drop-with-env
    native-with-drop
)

should_drop() {
    for step in "${dropping_steps[@]}"; do
        if [ "${BUILDKITE_STEP_KEY}" == "${step}" ]; then
            return 0
        fi
    done
    return 1
}

should_upload() {
    for step in "${uploading_steps[@]}"; do
        if [ "${BUILDKITE_STEP_KEY}" == "${step}" ]; then
            return 0
        fi
    done
    return 1
}

should_identify() {
    if [[ "${BUILDKITE_STEP_KEY}" =~ "native" ]]; then
        return 0
    else
        return 1
    fi
}

drop_role() {
    unset AWS_ACCESS_KEY_ID
    unset AWS_SECRET_ACCESS_KEY
    unset AWS_SESSION_TOKEN
}

if should_identify; then
    echo "--- :aws: Identity Before Packer"
    aws sts get-caller-identity
fi

echo "--- :packer: Packer build"
echo "THIS IS A TEST" > packer-manifest.json

if should_drop; then
    echo "--- Dropping role"
    drop_role
fi

if should_upload; then

    if should_identify; then
        echo "--- :aws: Identity before Upload (in command)"
        aws sts get-caller-identity
    fi

    echo "--- :buildkite: Uploading manifest"
    buildkite-agent artifact upload packer-manifest.json
fi
