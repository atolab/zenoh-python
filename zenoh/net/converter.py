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

def int_to_byte(i):
    return i.to_bytes(1, byteorder='big')


def byte_to_int(b):
    return int.from_bytes(b, byteorder='big', signed=False)
