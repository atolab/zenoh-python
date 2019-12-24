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
# Contributors: Gabriele Baldoni, ADLINK Technology Inc. - Zenoh API

import zenoh.net


class Data(object):
    def __init__(self, path, value, timestamp):
        self.path = path
        self.value = value
        self.timestamp = timestamp

    def __hash__(self):
        # As timestamp is unique per data, only hash the timestamp.
        return hash(self.timestamp)

    def __eq__(self, other):
        # As timestamp is unique per data, only compare timestamps.
        return self.timestamp.__eq__(other.timestamp)

    def __lt__(self, other):
        # order data according to timestamps
        return self.timestamp.__lt__(other.timestamp)

    def get_path(self):
        return self.path

    def get_value(self):
        return self.value

    def get_timestamp(self):
        return self.timestamp
