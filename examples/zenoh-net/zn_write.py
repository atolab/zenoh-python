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
# Contributors:
# Angelo Corsaro <angelo.corsaro@adlinktech.com>
# Olivier Hecart <olivier.hecart@adlinktech.com>
# Julien Enoch   <julien.enoch@adlinktech.com>

import sys
import time
from zenoh.net import Session


if __name__ == '__main__':
    uri = "/demo/example/zenoh-python-write"
    if len(sys.argv) > 1:
        uri = sys.argv[1]

    value = "Write from Python!"
    if len(sys.argv) > 2:
        value = sys.argv[2]

    locator = None
    if len(sys.argv) > 3:
        locator = sys.argv[3]

    print("Openning session...")
    s = Session.open(locator)

    print("Writing Data ('{}': '{}')...".format(uri, value))
    s.write_data(uri, bytes(value, encoding='utf8'))

    s.close()
