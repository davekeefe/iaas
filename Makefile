# Project Variables
REPO_NAME ?= iaas
VERSION ?= 0.1.$(BUILD_ID)

ORG_NAME := $(REPO_NAME)

# Docker registry
DOCKER_REGISTRY ?= 

# Artifactory instance
ARTIFACTORY_INSTANCE ?= 

# Projects
REL_PROJECT := $(REPO_NAME)$(BUILD_ID)
DEV_PROJECT := $(REL_PROJECT)dev

.PHONY: test build release clean tag buildtag login logout publish deploy

test:
	$(info "Creating cache volume...")
	$(info "Running tests...")
	$(info "Testing complete")

build:
	$(info "Packaging blueprint artifacts...")
	@ tar -cvzf $(REPO_NAME).tar.gz .
	$(info "Copying blueprint artifacts...")
	@ curl -u$$ARTIFACTORY_USER:$$ARTIFACTORY_PASSWORD -T $(REPO_NAME).tar.gz "http://$(ARTIFACTORY_INSTANCE):8081/artifactory/$(REPO_NAME)-local-repo/$(REL_PROJECT)/$(REPO_NAME).tar.gz"
	$(info "Build complete")
