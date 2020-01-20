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

from zenoh.net import Session, SubscriberMode
import time
import sys


def listener(rname, data, info):
    print("{}: {}".format(rname, data.decode()))


if __name__ == "__main__":
    locator = None
    if len(sys.argv) > 1:
        locator = sys.argv[1]

    s = Session.open(locator)
    sub = s.declare_subscriber('/myhome/kitcken/temp',
                               SubscriberMode.push(),
                               listener)

    # Listen for one minute and then exit
    time.sleep(120)
    s.undeclare_subscriber(sub)
    s.close()
