#
# Copyright (c) 2023 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from k8sapp_kubernetes_power_manager.common import constants as app_constants
from sysinv.tests.db import base as dbbase


class K8SAppKubernetesPowerManagerAppMixin(object):
    app_name = app_constants.HELM_APP_KUBERNETES_POWER_MANAGER
    path_name = app_name + '.tgz'

    def setUp(self):
        super(K8SAppKubernetesPowerManagerAppMixin, self).setUp()


# Test Configuration:
# - Controller
# - IPv6
# - Kubernetes Power Manager App
class K8sAppKubernetesPowerManagerControllerTestCase(
        K8SAppKubernetesPowerManagerAppMixin,
        dbbase.BaseIPv6Mixin,
        dbbase.ControllerHostTestCase):
    pass


# Test Configuration:
# - AIO
# - IPv4
# - Kubernetes Power Manager App
class K8SAppKubernetesPowerManagerAIOTestCase(
        K8SAppKubernetesPowerManagerAppMixin,
        dbbase.AIOSimplexHostTestCase):
    pass
