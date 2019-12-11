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

import re
import json
import zenoh.net
from enum import Enum
from zenoh.exceptions import ValidationError
from zenoh.encoding import Encoding


class ChangeKind(Enum):
    PUT = zenoh.net.Z_PUT
    UPDATE = zenoh.net.Z_UPDATE
    REMOVE = zenoh.net.Z_REMOVE


class Value(object):
    def __init__(self, value, encoding=Encoding.RAW, raw_format=""):
        if encoding is None:
            encoding = Encoding.RAW
        if encoding > Encoding.MAX:
            raise ValueError('Encoding not supported')
        if encoding == Encoding.PROTOBUF:
            raise ValueError('PROTOBUF Encoding not implemented')
        self.encoding = encoding
        if self.encoding == Encoding.JSON:
            if not (isinstance(value, dict) or isinstance(value, str)):
                raise ValidationError("Value is not a valid JSON")
            self.value = json.dumps(value)
        elif self.encoding == Encoding.RAW and isinstance(value, str):
            self.value = value.encode()
        else:
            self.value = value
        self.raw_format = raw_format

    def as_z_payload(self):
        if self.encoding == Encoding.RAW:
            return bytes(self.value)
        if self.encoding == Encoding.PROPERTY:
            s = ';'.join(map('='.join, map(list, self.value.items())))
            return s.encode()
        return self.value.encode()

    def get_encoding(self):
        return self.encoding

    def get_value(self):
        if self.encoding is Encoding.JSON:
            return json.loads(self.value)
        return self.value

    def __eq__(self, second_value):
        if isinstance(second_value, self.__class__):
            return self.value == second_value.value
        return False

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def from_z_resource(buf, info):
        encoding = Encoding.from_z_encoding(info.encoding)
        data = None
        if(encoding == Encoding.RAW):
            data = bytearray(buf)
        else:
            data = buf.decode()
        return Value(data, encoding)


class Change(object):
    kind_map = {
            zenoh.net.Z_PUT: ChangeKind.PUT,
            zenoh.net.Z_UPDATE: ChangeKind.UPDATE,
            zenoh.net.Z_REMOVE: ChangeKind.REMOVE
    }

    def __init__(self, path, kind, time, value=None):
        self.path = path
        self.time = time
        self.value = value
        if kind is None:
            self.kind = ChangeKind.PUT
        elif isinstance(kind, ChangeKind):
            self.kind = kind
        else:
            self.kind = Change.kind_map[kind]

    def get_path(self):
        return self.path

    def get_kind(self):
        return self.kind

    def get_time(self):
        return self.time

    def get_value(self):
        return self.value

    def __str__(self):
        return 'Path: {} Kind: {} Time: {} Value: {}'.format(
            self.path,
            self.kind,
            self.time,
            self.value)

    def __repr__(self):
        return self.__str__()
