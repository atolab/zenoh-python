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

from zenoh.net import Session
import random
import time
import sys

random.seed()


def read_temp():
    return random.randint(15, 30)


def run_sensor_loop(s, pub):
    # read and produce e temperature every half a second
    while True:
        t = read_temp()
        s.stream_data(pub, str(t).encode())
        time.sleep(0.1)


if __name__ == "__main__":
    locator = None
    if len(sys.argv) > 1:
        locator = sys.argv[1]

    s = Session.open(locator)
    pub = s.declare_publisher('/myhome/kitcken/temp')
    run_sensor_loop(s, pub)
