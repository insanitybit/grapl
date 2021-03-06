#!/usr/bin/env bash
# shellcheck disable=SC2034

# This file contains various constants that are used in more than one
# place in our pipeline scripts.
#
# They should all be marked as `readonly`, be named in
# SCREAMING_SNAKE_CASE, and ordered alphabetically when possible.
########################################################################

# This file contains a single flat JSON object describing
# artifact/version pairs for adding to the `artifacts` object in our
# Pulumi stack configuration files.
#
# When a pipeline generates artifacts, it should record this in a file
# of this name and upload it as a Buildkite artifact for consumption
# in other jobs.
readonly ARTIFACTS_FILE_SUFFIX=".artifacts.json"

# These are specified in `local.image_name`
readonly PACKER_IMAGE_NAME_SERVER="grapl-nomad-consul-server"
readonly PACKER_IMAGE_NAME_CLIENT="grapl-nomad-consul-client"
readonly PACKER_IMAGE_NAMES=(
    "${PACKER_IMAGE_NAME_SERVER}"
    "${PACKER_IMAGE_NAME_CLIENT}"
)

readonly PACKER_MANIFEST_SUFFIX=".packer-manifest.json"
