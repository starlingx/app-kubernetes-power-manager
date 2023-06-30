# README

This directory contains StarlingX chart that need to be built for this
application. The Helm Chart are derived from Kubernetes yaml files for
Kubernetes Power Manager.

The original sources were retrieved from:

https://github.com/intel/kubernetes-power-manager/archive/refs/tags/v2.3.0.tar.gz.

Additional information can be found at https://github.com/intel/kubernetes-power-manager/.

As the Kubernetes Power Manager versions are updated, maintainers of this repo
will need to update the helm chart.

## Install
1. Install the helm chart
helm install <release-name> /path/to/kubernetes-power-manager.tgz

2. Verify the instalation
helm list

3. Customize Configuration (Optional)
helm install -f custom-values.yaml <release-name> /path/to/kubernetes-power-manager.tgz
Use helm show values stx-platform/kubernetes-power-manager to list all possibilities.

This helm chart will install Kubernetes Power Manager CRDs and other manifests
needed to run power-operator on the controller and power-node-agent on each
available node.

## Test

To run properly, Node Feature Discovery (NFD) is required. After the
installation process of the Kubernetes Power Manager, the system must configured
in order to remove the Intel Max CState limitation from GRUB command line.

Use kubectl to show if the cstates are applyed
  kubectl get cstates -A
  kubectl get cstates controller-0 -n intel-power -o yaml
