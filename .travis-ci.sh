#!/usr/bin/env bash

WD=$(pwd)
cd $(mktemp -d)
RD=$(pwd)
curl -L -o zenohd https://github.com/atolab/atobin/raw/master/zenoh/unstable/ubuntu/16.04/zenohd
curl -L -o zenoh-plugin-storages.cmxs https://github.com/atolab/atobin/raw/master/zenoh-storages/unstable/ubuntu/16.04/zenoh-plugin-storages.cmxs
chmod +x $RD/zenohd
chmod +x $RD/zenoh-plugin-storages.cmxs
$RD/zenohd -P "$RD/zenoh-plugin-storages.cmxs -w" --verbosity=debug > $RD/zenohd.out 2>&1 & echo $! > $RD/zenohd.pid
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