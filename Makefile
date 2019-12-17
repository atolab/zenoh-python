# Copyright (c) 2018 ADLINK Technology Inc.
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# http://www.eclipse.org/legal/epl-2.0, or the Apache License, Version 2.0
# which is available at https://www.apache.org/licenses/LICENSE-2.0.
#
# SPDX-License-Identifier: EPL-2.0 OR Apache-2.0
#
# Contributors: Gabriele Baldoni, ADLINK Technology Inc. - Initial commit

# -*-Makefile-*-

WD := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))));

all:
	echo "Nothing to do";

install:
	python3 setup.py install --record zenoh_files.txt


dist:
	python3 setup.py sdist bdist_wheel

clean:
	rm -rf ./build ./dist ./zenoh.egg-info .coverage;
	rm -rf zenoh_api.log .tox zenoh.egg-info ./zenoh/__pycache__/ ./zenoh/*/__pycache__/ ./zenoh/*/*/__pycache__/;

test:
	rm -rf ./tox
	tox

doc:
	cd docs && $(MAKE) clean
	cd docs && $(MAKE) latexpdf
	cd docs && $(MAKE) dirhtml
