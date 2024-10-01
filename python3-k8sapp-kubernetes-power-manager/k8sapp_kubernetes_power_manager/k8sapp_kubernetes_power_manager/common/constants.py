#
# Copyright (c) 2023-2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#

HELM_APP_KUBERNETES_POWER_MANAGER = 'kubernetes-power-manager'
HELM_RELEASE_KUBERNETES_POWER_MANAGER = 'kubernetes-power-manager'
HELM_CHART_KUBERNETES_POWER_MANAGER = 'kubernetes-power-manager'
HELM_NS_KUBERNETES_POWER_MANAGER = 'intel-power'
HELM_APP_KUBERNETES_POWER_MANAGER_AGENT = 'power-node-agent'

HELM_APP_KUBERNETES_POWER_MANAGER_CRD_CSTATES = 'cstates.power.intel.com'
HELM_APP_KUBERNETES_POWER_MANAGER_CRD_POWERCONFIGS = 'powerconfigs.power.intel.com'
HELM_APP_KUBERNETES_POWER_MANAGER_CRD_POWERNODES = 'powernodes.power.intel.com'
HELM_APP_KUBERNETES_POWER_MANAGER_CRD_POWERPODS = 'powerpods.power.intel.com'
HELM_APP_KUBERNETES_POWER_MANAGER_CRD_POWERPROFILES = 'powerprofiles.power.intel.com'
HELM_APP_KUBERNETES_POWER_MANAGER_CRD_POWERWORKLOADS = 'powerworkloads.power.intel.com'
HELM_APP_KUBERNETES_POWER_MANAGER_CRD_TIMEOFDAYCRONJOBS = 'timeofdaycronjobs.power.intel.com'
HELM_APP_KUBERNETES_POWER_MANAGER_CRD_TIMEOFDAYS = 'timeofdays.power.intel.com'
HELM_APP_KUBERNETES_POWER_MANAGER_CRD_UNCORES = 'uncores.power.intel.com'

POWERWORKLOADS_PATCH = """ # noqa: E501
spec:
  versions:
  - name: v1
    schema:
      openAPIV3Schema:
        description: PowerWorkload is the Schema for the powerworkloads API
        properties:
          apiVersion:
            description: 'APIVersion defines the versioned schema of this representation
              of an object. Servers should convert recognized schemas to the latest
              internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#resources'
            type: string
          kind:
            description: 'Kind is a string value representing the REST resource this
              object represents. Servers may infer this from the endpoint the client
              submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/sig-architecture/api-conventions.md#types-kinds'
            type: string
          metadata:
            type: object
          spec:
            description: PowerWorkloadSpec defines the desired state of PowerWorkload
            properties:
              allCores:
                description: AllCores determines if the Workload is to be applied
                  to all cores (i.e. use the Default Workload)
                type: boolean
              name:
                description: The name of the workload
                type: string
              powerNodeSelector:
                additionalProperties:
                  type: string
                description: The labels signifying the nodes the user wants to use
                type: object
              powerProfile:
                description: PowerProfile is the Profile that this PowerWorkload is
                  based on
                type: string
              reservedCPUs:
                description: Reserved CPUs are the CPUs that have been reserved by
                  Kubelet for use by the Kubernetes admin process This list must match
                  the list in the user's Kubelet configuration
                items:
                  properties:
                    cores:
                      items:
                        type: integer
                      type: array
                    powerProfile:
                      type: string
                  required:
                  - cores
                  type: object
                type: array
              workloadNodes:
                properties:
                  containers:
                    items:
                      properties:
                        exclusiveCpus:
                          description: The exclusive CPUs given to this Container
                          items:
                            type: integer
                          type: array
                        id:
                          description: The ID of the Container
                          type: string
                        name:
                          description: The name of the Container
                          type: string
                        pod:
                          description: The name of the Pod the Container is running
                            on
                          type: string
                        powerProfile:
                          description: The PowerProfile that the Container is utilizing
                          type: string
                        workload:
                          description: The PowerWorkload that the Container is utilizing
                          type: string
                      type: object
                    type: array
                  cpuIds:
                    items:
                      type: integer
                    type: array
                  name:
                    type: string
                type: object
            required:
            - name
            type: object
          status:
            description: PowerWorkloadStatus defines the observed state of PowerWorkload
            properties:
              'node:':
                description: The Node that this Shared PowerWorkload is associated
                  with
                type: string
            type: object
        type: object
    served: true
    storage: true
"""

HELM_APP_KUBERNETES_POWER_MANAGER_CRDS = [
    HELM_APP_KUBERNETES_POWER_MANAGER_CRD_CSTATES,
    HELM_APP_KUBERNETES_POWER_MANAGER_CRD_POWERCONFIGS,
    HELM_APP_KUBERNETES_POWER_MANAGER_CRD_POWERNODES,
    HELM_APP_KUBERNETES_POWER_MANAGER_CRD_POWERPODS,
    HELM_APP_KUBERNETES_POWER_MANAGER_CRD_POWERPROFILES,
    HELM_APP_KUBERNETES_POWER_MANAGER_CRD_POWERWORKLOADS,
    HELM_APP_KUBERNETES_POWER_MANAGER_CRD_TIMEOFDAYCRONJOBS,
    HELM_APP_KUBERNETES_POWER_MANAGER_CRD_TIMEOFDAYS,
    HELM_APP_KUBERNETES_POWER_MANAGER_CRD_UNCORES
]

HELM_COMPONENT_LABEL = 'app.starlingx.io/component'
HELM_NFD_REQUIRED_PARAM = 'nfd-required'

# These parameters refer to the Node Feature Discovery (NFD) application.
# They should be kept in sync.
# https://opendev.org/starlingx/app-node-feature-discovery.
HELM_APP_NFD = 'node-feature-discovery'
HELM_NS_NFD = 'node-feature-discovery'
HELM_CHART_NFD = 'node-feature-discovery'

APPLICATION_CSTATE = "C1"
CSTATE_C0 = "POLL"
PLATFORM_CSTATE = "C6"
