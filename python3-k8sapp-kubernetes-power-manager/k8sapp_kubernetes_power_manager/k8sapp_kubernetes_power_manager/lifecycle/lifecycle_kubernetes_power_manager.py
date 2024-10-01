#
# Copyright (c) 2023-2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

""" System inventory App lifecycle operator."""
import yaml

from k8sapp_kubernetes_power_manager.common import constants as app_constants

from oslo_log import log as logging
from sysinv.common import constants as cst
from sysinv.common import exception
from sysinv.helm import lifecycle_base as base


LOG = logging.getLogger(__name__)


class KubernetesPowerManagerAppLifecycleOperator(base.AppLifecycleOperator):
    def app_lifecycle_actions(self, context, conductor_obj, app_op,
                              app, hook_info):
        """Perform lifecycle actions for an operation

        :param context: request context, can be None
        :param conductor_obj: conductor object, can be None
        :param app_op: AppOperator object
        :param app: AppOperator.Application object
        :param hook_info: LifecycleHookInfo object

        """

        # Semantic Check
        if (hook_info.lifecycle_type == cst.APP_LIFECYCLE_TYPE_SEMANTIC_CHECK
                and hook_info.operation == cst.APP_APPLY_OP
                and hook_info.relative_timing == cst.APP_LIFECYCLE_TIMING_PRE):
            return self._pre_semantic_check(app, app_op)

        # FluxCD Request
        if (hook_info.lifecycle_type == cst.APP_LIFECYCLE_TYPE_FLUXCD_REQUEST
                and hook_info.operation == cst.APP_APPLY_OP
                and hook_info.relative_timing == cst.APP_LIFECYCLE_TIMING_PRE):
            return self._pre_fluxcd_request(app, app_op)

        # Operation
        if (hook_info.lifecycle_type == cst.APP_LIFECYCLE_TYPE_OPERATION
                and hook_info.operation == cst.APP_REMOVE_OP
                and hook_info.relative_timing == cst.APP_LIFECYCLE_TIMING_POST):
            return self._post_remove(app, app_op)

        # Update Request
        if (hook_info.lifecycle_type == cst.APP_LIFECYCLE_TYPE_SEMANTIC_CHECK
                and hook_info.operation == cst.APP_UPDATE_OP
                and hook_info.relative_timing == cst.APP_LIFECYCLE_TIMING_PRE):
            return self._pre_update(hook_info, app, app_op)

        super(KubernetesPowerManagerAppLifecycleOperator,
              self).app_lifecycle_actions(
            context, conductor_obj, app_op, app, hook_info
        )

    def _pre_fluxcd_request(self, app, app_op):
        LOG.debug(f"Executing pre_fluxcd_request for {app.name} app")

        # Applying label on namespace before running FluxCD manifests
        # to ensure that all pods in this namespace run on correct cores
        self._update_component_label(app, app_op)

    def _pre_semantic_check(self, app, app_op):
        LOG.debug(f"Executing pre_semantic_check for {app.name} app")

        dbapi = app_op._dbapi
        try:
            nfd_kube_app = dbapi.kube_app_get(app_constants.HELM_APP_NFD)
            LOG.info("Node Feature Discovery (NFD) Application found - "
                     f"Version: {nfd_kube_app.app_version} - "
                     "Status: {nfd_kube_app.status}")

            nfd_installed = nfd_kube_app.status == cst.APP_APPLY_SUCCESS

        except exception.KubeAppNotFound:
            nfd_installed = False

        if not nfd_installed:
            if self._is_nfd_required(dbapi):
                raise exception.LifecycleSemanticCheckException(
                    "Node Feature Discovery (NFD) Application is required. "
                    "You can bypass this check by setting the "
                    f"{app_constants.HELM_NFD_REQUIRED_PARAM} parameter to "
                    "False using overrides.")

            LOG.info("Bypass flag for Node Feature Discovery (NFD) "
                     "Application found.")

    def _post_remove(self, app, app_op):
        LOG.debug(f"Executing post_remove for {app.name} app")

        k8s_client_core = app_op._kube._get_kubernetesclient_core()
        k8s_client_ext = app_op._kube._get_kubernetesclient_extensions()

        # Remove all daemonsets (agents) started by the controller and any
        # orphan pods in namespace
        self._delete_pods(app_op, k8s_client_core)

        # Helm doesn't remove CRDs. To clean up after application-remove,
        # we need to explicitly delete the CRDs
        try:
            for crd in app_constants.HELM_APP_KUBERNETES_POWER_MANAGER_CRDS:
                k8s_client_ext.delete_custom_resource_definition(name=crd)
        except Exception as ex:
            LOG.error(f"An error occur during the CRDs removal."
                      f"{ex}")

        # Remove the namespace
        app_op._kube.kube_delete_namespace(
            app_constants.HELM_NS_KUBERNETES_POWER_MANAGER)

    def _is_nfd_required(self, dbapi):

        """Checks the state of the parameter that controls whether the NFD
        application is required

        :param dbapi: dbapi
        :return True if enabled otherwise False
        """
        val = True
        try:
            app = dbapi.kube_app_get(
                app_constants.HELM_APP_KUBERNETES_POWER_MANAGER)

            user_overrides = self._get_user_overrides(app, dbapi)
            if app_constants.HELM_NFD_REQUIRED_PARAM in user_overrides:
                if isinstance(
                        user_overrides[app_constants.HELM_NFD_REQUIRED_PARAM],
                        bool):
                    val = user_overrides[app_constants.HELM_NFD_REQUIRED_PARAM]

                LOG.error(f"The value of parameter "
                          f"{app_constants.HELM_NFD_REQUIRED_PARAM} must be "
                          "true or false.")

        except exception.KubeAppNotFound as e:
            LOG.error("Failed to access app info "
                      f"{app_constants.HELM_APP_KUBERNETES_POWER_MANAGER}: "
                      f"{e}")

        except exception.HelmOverrideNotFound as e:
            LOG.error("Failed to access user overrides from chart "
                      f"{app_constants.HELM_CHART_KUBERNETES_POWER_MANAGER}: "
                      f"{e}")

        return val

    def _update_component_label(self, app, app_op):
        """Create the StarlingX component label in namespace

        :param app_op: AppOperator object
        :param app: AppOperator.Application object
        """

        user_overrides = self._get_user_overrides(app._kube_app, app_op._dbapi)
        component_label = user_overrides.get(
            app_constants.HELM_COMPONENT_LABEL,
            'platform')

        if component_label in ['application', 'platform']:
            # Get namespace attributes
            k8s_client_core = app_op._kube._get_kubernetesclient_core()
            namespace = k8s_client_core.read_namespace(
                app_constants.HELM_NS_KUBERNETES_POWER_MANAGER)

            # Previous value
            previous_component_label = namespace.metadata.labels.get(
                app_constants.HELM_COMPONENT_LABEL)

            # Set label in namespace
            namespace.metadata.labels.update(
                {
                    app_constants.HELM_COMPONENT_LABEL:
                    component_label
                })
            app_op._kube.kube_patch_namespace(
                app_constants.HELM_NS_KUBERNETES_POWER_MANAGER,
                namespace)

            # Restarts all pods in namespace if label has changed
            if (previous_component_label is not None and
                    previous_component_label != component_label):
                self._delete_pods(app_op, k8s_client_core)

        else:
            raise ValueError(f"Value {component_label} for label:namespace"
                             f"{app_constants.HELM_COMPONENT_LABEL}:"
                             f"{app_constants.HELM_NS_KUBERNETES_POWER_MANAGER}"
                             " is not supported")

    def _get_user_overrides(self, kube_app, dbapi):
        """Get user overrides from db

        :param kube_app: Kubernetes Application instance
        :param dbapi: dbapi
        :return User overrides in dict format
        """

        user_overrides = {}

        overrides = dbapi.helm_override_get(
            kube_app.id,
            app_constants.HELM_CHART_KUBERNETES_POWER_MANAGER,
            app_constants.HELM_NS_KUBERNETES_POWER_MANAGER)

        if overrides.user_overrides:
            user_overrides = yaml.safe_load(overrides.user_overrides)

        return user_overrides

    def _delete_pods(self, app_op, k8s_client_core):
        """Delete all pods within the application namespace

        :param app_op: AppOperator object
        :param k8s_client_core: Kubernetes client object
        """

        try:
            # pod list
            pods = k8s_client_core.list_namespaced_pod(
                app_constants.HELM_NS_KUBERNETES_POWER_MANAGER)

            # On namespace label change, delete pods to force restart
            for pod in pods.items:
                app_op._kube.kube_delete_pod(
                    name=pod.metadata.name,
                    namespace=app_constants.HELM_NS_KUBERNETES_POWER_MANAGER,
                    grace_periods_seconds=0
                )

        except Exception:
            LOG.error("Failed to delete pods in namespace %s",
                      app_constants.HELM_NS_KUBERNETES_POWER_MANAGER)

    def _pre_update(self, hook_info, app, app_op):
        """Patch the Power Workload CRD to enable the update

        :param hook_info: LifecycleHookInfo object
        :param app: AppOperator.Application object
        :param app_op: AppOperator object
        """

        if app.status == cst.APP_APPLY_SUCCESS:
            return

        LOG.debug(f"Running app update to {app.version} version")
        try:
            body = yaml.safe_load(app_constants.POWERWORKLOADS_PATCH)

            k8s_client_ext = app_op._kube._get_kubernetesclient_extensions()
            k8s_client_ext.patch_custom_resource_definition(
                name=(app_constants.
                      HELM_APP_KUBERNETES_POWER_MANAGER_CRD_POWERWORKLOADS),
                body=body,
            )
        except Exception as ex:
            LOG.error("Failed to path PowerWorkload resource "
                      "during app update."
                      f"{ex}")
