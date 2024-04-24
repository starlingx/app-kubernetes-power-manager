#
# Copyright 2017 The Openstack-Helm Authors.
#
# Copyright (c) 2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
# It's necessary to set this because some environments don't link sh -> bash.
SHELL := /bin/bash
TASK  := build

EXCLUDES := helm-toolkit doc tests tools logs tmp
CHARTS := helm-toolkit $(filter-out $(EXCLUDES), $(patsubst %/.,%,$(wildcard */.)))
HELM_DIR := kubernetes-power-manager/helm/kubernetes-power-manager

.PHONY: $(EXCLUDES) $(CHARTS)

all: $(CHARTS)

$(CHARTS):
	@if [ -d $@ ]; then \
		echo; \
		echo "===== Processing [$@] chart ====="; \
		make $(TASK)-$@; \
	fi

init-%:
	if [ -f $*/Makefile ]; then make -C $*; fi

lint-%: init-%
	if [ -d $* ]; then helm lint $(HELM_DIR); fi

build-%: lint-%
	if [ -d $* ]; then \
		helm package $(HELM_DIR) --version $(CHART_BASE_VERSION) --app-version $(CHART_APP_VERSION); \
	fi

clean:
	@echo "Clean all build artifacts"
	rm -f */templates/_partials.tpl */templates/_globals.tpl
	rm -rf */charts */tmpcharts

%:
	@:
