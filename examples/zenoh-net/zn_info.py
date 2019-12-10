import sys
import time
import binascii
import zenoh
from zenoh.net import Session


if __name__ == '__main__':
    locator = None
    if len(sys.argv) > 1:
        locator = sys.argv[1]

    print("Openning session...")
    s = Session.open(locator, {zenoh.Z_USER_KEY: "user".encode(),
                               zenoh.Z_PASSWD_KEY: "password".encode()})

    info = s.info()
    peer = info[zenoh.Z_INFO_PEER_KEY]
    pid = info[zenoh.Z_INFO_PID_KEY]
    peer_pid = info[zenoh.Z_INFO_PEER_PID_KEY]
    print("LOCATOR :  {}".format(peer.decode("utf-8")))
    print("PID :      {}".format(binascii.hexlify(pid).decode("ascii")))
    print("PEER PID : {}".format(binascii.hexlify(peer_pid).decode("ascii")))

    s.close()
