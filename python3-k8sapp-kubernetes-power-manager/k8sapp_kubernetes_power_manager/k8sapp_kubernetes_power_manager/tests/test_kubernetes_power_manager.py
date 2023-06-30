#
# Copyright (c) 2023 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from k8sapp_kubernetes_power_manager.tests import test_plugins

from sysinv.db import api as dbapi
from sysinv.tests.db import base as dbbase
from sysinv.tests.db import utils as dbutils
from sysinv.tests.helm import base


class KubernetesPowerManagerTestCase(
        test_plugins.K8SAppKubernetesPowerManagerAppMixin,
        base.HelmTestCaseMixin):

    def setUp(self):
        super(KubernetesPowerManagerTestCase, self).setUp()
        self.app = dbutils.create_test_app(name='kubernetes-power-manager')
        self.dbapi = dbapi.get_instance()


class KubernetesPowerManagerTestCaseDummy(
        KubernetesPowerManagerTestCase,
        dbbase.ProvisionedControllerHostTestCase):
    # without a test zuul will fail
    def test_dummy(self):
        pass
