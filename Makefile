#
# Door-backend Makefile
#

SHELL := /bin/bash

NOW := $(shell date +"%Y-%m-%d %H:%M:%S")
PROJECT := Door-backend
PKG_NAME := $(PROJECT).tar.gz


all : install pkg clean
.PHONY: all

install:
	@echo -e "\033[32m$(NOW): Build ${PROJECT} project\033[0m"

pkg:
	@echo -e "\033[32m$(NOW): start packing\033[0m"

clean:
	@echo -e "\033[32m$(NOW): clean some dir\033[0m"
