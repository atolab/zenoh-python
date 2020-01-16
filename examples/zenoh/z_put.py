# Copyright (c) 2014, 2020 Contributors to the Eclipse Foundation
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
# Contributors: Julien Enoch, ADLINK Technology Inc.
# Initial implementation of Eclipse Zenoh.

import sys
from zenoh import Zenoh, Selector, Path, Workspace, Encoding, Value

# If not specified as 1st argument, use a relative path
# (to the workspace below): 'zenoh-python-put'
path = 'zenoh-python-put'
if len(sys.argv) > 1:
    path = sys.argv[1]

value = 'Put from Zenoh Python!'
if len(sys.argv) > 2:
    value = sys.argv[2]

locator = None
if len(sys.argv) > 3:
    locator = sys.argv[3]

print('Login to Zenoh (locator={})...'.format(locator))
z = Zenoh.login(locator)

print('Use Workspace on "/demo/example"')
w = z.workspace('/demo/example')

print('Put on {} : {}'.format(path, value))
w.put(path, Value(value, encoding=Encoding.STRING))

z.logout()
