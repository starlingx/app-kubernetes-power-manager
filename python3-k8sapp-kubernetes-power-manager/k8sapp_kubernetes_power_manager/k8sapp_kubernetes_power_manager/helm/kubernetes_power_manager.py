#
# Copyright (c) 2023-2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

from k8sapp_kubernetes_power_manager.common import constants as app_constants

from oslo_log import log as logging
from sysinv.common import constants
from sysinv.common import exception
from sysinv.common import kubernetes
from sysinv.db import api as sys_dbapi
from sysinv.helm import base


LOG = logging.getLogger(__name__)


class KubernetesPowerManagerHelm(base.FluxCDBaseHelm):

    CHART = app_constants.HELM_CHART_KUBERNETES_POWER_MANAGER
    HELM_RELEASE = app_constants.HELM_RELEASE_KUBERNETES_POWER_MANAGER
    SERVICE_NAME = 'kubernetes-power-manager'

    SUPPORTED_NAMESPACES = base.BaseHelm.SUPPORTED_NAMESPACES + \
        [app_constants.HELM_NS_KUBERNETES_POWER_MANAGER]

    SUPPORTED_APP_NAMESPACES = {
        app_constants.HELM_APP_KUBERNETES_POWER_MANAGER:
            (base.BaseHelm.SUPPORTED_NAMESPACES +
             [app_constants.HELM_NS_KUBERNETES_POWER_MANAGER]),
    }

    def get_namespaces(self):
        return self.SUPPORTED_NAMESPACES

    def get_overrides(self, namespace=None):
        ihosts = self._get_admissible_ihosts()

        overrides = {
            app_constants.HELM_NS_KUBERNETES_POWER_MANAGER: {
                'sharedProfile': self._get_shared_profile_override(ihosts),
                'cstatesProfile': self._get_cstates_override(ihosts)
            }
        }

        if namespace in self.SUPPORTED_NAMESPACES:
            return overrides[namespace]

        if namespace:
            raise exception.InvalidHelmNamespace(chart=self.CHART,
                                                 namespace=namespace)

        return overrides

    def _get_platform_cpus_from_host(self, host_uuid):
        """Return a list of platform cpus of a host

        Args:
            host_uuid: The UUID of a host

        Returns:
            list: A list of platform cpus
        """
        dbapi = sys_dbapi.get_instance()
        icpus = dbapi.icpu_get_by_ihost(host_uuid)
        platform_cpus = []
        for icpu in icpus:
            allocated_function = icpu.get('allocated_function')
            if allocated_function == constants.PLATFORM_FUNCTION:
                platform_cpus.append(int(icpu.cpu))
        return platform_cpus

    def _get_shared_profile_override(self, ihosts):
        """Return a dictionary with Shared Profile information.

        Args:
            ihosts: The list of ihosts of the cluster

        Returns:
            dict: Dictionary with min, max, reserved_cpus, and governor
            key/values
        """
        override = {}
        for ihost in ihosts:
            if (ihost.min_cpu_mhz_allowed is None or
                    ihost.max_cpu_mhz_allowed is None):
                continue

            override[ihost.hostname] = {
                'min': int(ihost.min_cpu_mhz_allowed),
                'max': int(ihost.max_cpu_mhz_allowed),
                "reservedCPUs": '{}'.format(
                    self._get_platform_cpus_from_host(ihost.uuid)
                ),
                'governor': 'performance',
                'shared': True,
                'reservedProfile': 'shared-{}'.format(
                    ihost.hostname
                )
            }
        return override

    def _get_cstates_override(self, ihosts):
        """Return a dictionary with CStates information, organized by pool type

        Args:
            ihosts: The list of ihosts of the cluster

        Returns:
            dict: Dictionary with sharedPoolCstates and individualCoreCStates
            dictionaries
        """
        override = {}

        for ihost in ihosts:
            if ihost.cstates_available is None:
                continue

            cstates_list = ihost.cstates_available.split(',')

            override[ihost.hostname] = {
                "sharedPoolCStates": self._make_shared_object(cstates_list),
                "individualCoreCStates": self._make_cpu_object(
                    cstates_list,
                    self._get_platform_cpus_from_host(ihost.uuid)
                )
            }

        return override

    def _make_shared_object(self, cstates):
        """Return the CPU object for CState override construction

        Args:
            cstates (list): The list of CStates available on the host

        Returns:
            dict: Dictionary that contains the CState set for Shared Pool.
        """
        # If CPU list is empty we need to prepare the Shared Pool block
        new_cpu_dict = {}
        target_cstate = None

        # Get the APPLICATION_CSTATE name, or the highest CState number
        if [cstate for cstate in cstates if
                app_constants.APPLICATION_CSTATE in cstate]:
            target_cstate = [cstate for cstate in cstates if
                             app_constants.APPLICATION_CSTATE in cstate][0]
        else:
            target_cstate = (app_constants.CSTATE_C0
                             if app_constants.CSTATE_C0 in cstates
                             else cstates[0])

        target = True
        for cstate in cstates:
            if cstate == app_constants.CSTATE_C0:
                new_cpu_dict[cstate] = True
                continue
            new_cpu_dict[cstate] = target
            if cstate == target_cstate:
                target = False

        return new_cpu_dict

    def _make_cpu_object(self, cstates, cpu_list):
        """Return the CPU object for CState override construction

        Args:
            cstates (list): The list of CStates available on the host
            cpu_list (list): The list of platforma cpus

        Returns:
            dict: Dictionary that contains the CState set for Individual Cores
            C States
        """
        # If CPU list is empty we need to prepare the Shared Pool block
        new_cpu_dict = {}
        target_cstate = None

        # Get the PLATFORM_CSTATE name, or the lowest CState number
        if [cstate for cstate in cstates if
                app_constants.PLATFORM_CSTATE in cstate]:
            target_cstate = [cstate for cstate in cstates if
                             app_constants.PLATFORM_CSTATE in cstate][0]
        else:
            target_cstate = cstates[-2]

        cstate_dic = {}
        target = True
        for cstate in cstates:
            if cstate == app_constants.CSTATE_C0:
                cstate_dic[cstate] = True
                continue
            cstate_dic[cstate] = target
            if cstate == target_cstate:
                target = False

        for cpu_add in cpu_list:
            new_cpu_dict[str(cpu_add)] = cstate_dic

        return new_cpu_dict

    def _get_admissible_ihosts(self):
        """Return "power-management" labeled ihosts"""
        kube = kubernetes.KubeOperator()
        nodes = kube.kube_get_nodes()
        dbapi = sys_dbapi.get_instance()
        ihosts = []
        for node in nodes:
            node_labels = node.metadata.labels
            if constants.KUBE_POWER_MANAGER_LABEL in node_labels:
                ihosts.append(
                    dbapi.ihost_get_by_hostname(node.metadata.name))

        return ihosts
