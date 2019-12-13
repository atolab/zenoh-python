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
# Contributors: Angelo Corsaro, ADLINK Technology Inc. - Zenoh API refactoring

from zenoh.workspace import Workspace
from zenoh.admin import *
import threading
from zenoh.net import Session, ZN_INFO_PEER_PID_KEY


class Zenoh(object):
    '''

    The Zenoh client API.

    '''

    ZENOH_DEFAULT_PORT = 7447

    def __init__(self, rt):
        self.rt = rt

    @staticmethod
    def login(locator, properties=None):
        '''

        Establish a session with the Zenoh router reachable via provided
        Zenoh locator. If the provided locator is ``None``, :func:`login`
        will perform some dynamic discovery and try to establish the session
        automatically. When not ``None``, the locator must have the format:
        ``tcp/<ip>:<port>``.

        :param locator: a Zenoh locator or ``None``.
        :param properties: the Properties to be used for this session
            (e.g. "user", "password", ...). Can be ``None``.
        :returns: a Zenoh object.

        '''
        zprops = {} if properties is None else {
            zenoh.net.ZN_USER_KEY if k == "user" else
            zenoh.net.ZN_PASSWORD_KEY: val
            for k, val in properties.items()
            if k == "user" or key == "password"}

        return Zenoh(Session.open(locator, zprops))

    def workspace(self, path, executor=None):
        '''

        Creates a :class:`~zenoh.workspace.Workspace` using the
        provided path. All relative Selector or Path used with this
        :class:`~zenoh.workspace.Workspace` will be relative to
        this path.

        :param path: the Workspace's path.
        :param executor: an executor of type
            :py:class:`concurrent.futures.Executor` or ``None``.
            If not ``None``, all subscription listeners and eval callbacks are
            executed by the provided executor. This is useful when listeners
            and/or callbacks need to perform long operations or need to call
            operations like :func:`~zenoh.workspace.Workspace.get`.
        :returns: a :class:`~zenoh.workspace.Workspace`.

        '''
        return Workspace(self.rt, path, executor)

    def logout(self):
        '''

        Terminates this session.

        '''
        self.rt.close()

    def admin(self):
        '''

        Creates an admin workspace that provides helper operations to
        administer Zenoh.

        '''
        return Admin(self.workspace(
            '/{}/{}'.format(
                Admin.PREFIX,
                ''.join('{:02x}'.format(x) for x in
                        self.rt.info()[ZN_INFO_PEER_PID_KEY]))))