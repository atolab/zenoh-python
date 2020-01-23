#!/usr/bin/env bash

#
# Copyright (c) 2017, 2020 ADLINK Technology Inc.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License 2.0 which is available at
# http://www.eclipse.org/legal/epl-2.0, or the Apache License, Version 2.0
# which is available at https://www.apache.org/licenses/LICENSE-2.0.
#
# SPDX-License-Identifier: EPL-2.0 OR Apache-2.0
#
# Contributors:
#   ADLINK zenoh team, <zenoh@adlink-labs.tech>
#

WD=$(pwd)
cd $(mktemp -d)
RD=$(pwd)
curl -L -o zenohd https://github.com/atolab/atobin/raw/master/zenoh/unstable/ubuntu/18.04/zenohd
curl -L -o zenoh-plugin-storages.cmxs https://github.com/atolab/atobin/raw/master/zenoh-storages/unstable/ubuntu/18.04/zenoh-plugin-storages.cmxs
chmod +x $RD/zenohd
chmod +x $RD/zenoh-plugin-storages.cmxs
$RD/zenohd -P "$RD/zenoh-plugin-storages.cmxs" --verbosity=debug > $RD/zenohd.out 2>&1 & echo $! > $RD/zenohd.pid
ZPID=$(<"$RD/zenohd.pid")
sleep 2;
cat $RD/zenohd.out
echo "ZENOHD PID $ZPID"
cd $WD
echo "Running tests from $WD"
tox
echo "KILLING ZENOHD $ZPID"
kill -15 $ZPID
rm -rf $RD
exit 0
