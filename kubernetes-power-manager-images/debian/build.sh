#!/bin/sh
#
# Copyright (c) 2023 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

IMAGE=$1
IMAGE_TAG=$2

echo "=============== build script ================"
echo image: "${IMAGE}"
echo image_tag: "${IMAGE_TAG}"
pwd

if [ -z "${IMAGE_TAG}" ]; then
    echo "Image tag must be specified. build ${IMAGE} Aborting..." >&2
    exit 1
fi

build_power_operator_image() {
    export POWER_OPERATOR_IMAGE=$1
    echo "power_operator_image: ${POWER_OPERATOR_IMAGE}"
    pwd
    docker build -t "${POWER_OPERATOR_IMAGE}" -f build/Dockerfile .
    echo "power-operator image build done"
    return 0
}

build_power_node_agent_image() {
    export POWER_NODE_AGENT_IMAGE=$1
    echo "power_node_agent_image: ${POWER_NODE_AGENT_IMAGE}"
    pwd
    docker build -t "${POWER_NODE_AGENT_IMAGE}" -f build/Dockerfile.nodeagent .
    echo "power-node-agent image build done"
    return 0
}

case ${IMAGE} in
    power_operator)
        echo "Build image: power-operator"
        build_power_operator_image "${IMAGE_TAG}"
        ;;
    power_node_agent)
        echo "build image: power-node-agent"
        build_power_node_agent_image "${IMAGE_TAG}"
        ;;
    *)
        echo "Unsupported ARGS in ${0}: ${IMAGE}" >&2
        exit 1
        ;;
esac

exit 0
