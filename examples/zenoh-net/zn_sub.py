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
from zenoh.net import Session, SubscriberMode


def listener(rname, data, info):
    print(">> [Subscription listener] Received ('{}': '{}') at {}"
          .format(rname, data.decode("utf-8"), info.tstamp))


if __name__ == '__main__':
    uri = "/demo/example/**"
    if len(sys.argv) > 1:
        uri = sys.argv[1]

    locator = None
    if len(sys.argv) > 2:
        locator = sys.argv[2]

    print("Openning session...")
    s = Session.open(locator)

    print("Declaring Subscriber on '{}'...".format(uri))
    sub = s.declare_subscriber(uri, SubscriberMode.push(), listener)

    c = '\0'
    while c != 'q':
        c = sys.stdin.read(1)

    s.undeclare_subscriber(sub)
    s.close()
