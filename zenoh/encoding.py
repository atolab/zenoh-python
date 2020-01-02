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

# Encoding

from enum import Enum


class Encoding(Enum):
    '''
    A description of the :class:`Value` format, allowing zenoh to know
    how to encode/decode the value to/from a bytes buffer.
    '''

    RAW = 0x00
    '''
    The value has a RAW encoding (i.e. it's a bytes buffer).
    '''

    STRING = 0x02
    '''
    The value is an UTF-8 string.
    '''

    PROPERTIES = 0x3
    '''
    The value if a list of keys/values, encoded as an UTF-8 string.
    The keys/values are separated by ';' character, and each key is separated
    from its associated value (if any) with a '=' character.
    '''

    JSON = 0x04
    '''
    The value is a JSON structure in an UTF-8 string.
    '''


class TranscodingFallback(Enum):
    FAIL = 0x01
    DROP = 0x02
    KEEP = 0x03
