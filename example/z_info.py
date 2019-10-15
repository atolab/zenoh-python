import sys
import time
import binascii
import zenoh
from zenoh import Zenoh


if __name__ == '__main__':
    locator = "tcp/127.0.0.1:7447"
    if len(sys.argv) > 1:
        locator = sys.argv[1]

    print("Connecting to {}...".format(locator))
    z = Zenoh.open(locator, {zenoh.Z_USER_KEY: "user".encode(),
                             zenoh.Z_PASSWD_KEY: "password".encode()})

    info = z.info()
    peer = info[zenoh.Z_INFO_PEER_KEY]
    pid = info[zenoh.Z_INFO_PID_KEY]
    peer_pid = info[zenoh.Z_INFO_PEER_PID_KEY]
    print("LOCATOR :  {}".format(peer.decode("utf-8")))
    print("PID :      {}".format(binascii.hexlify(pid).decode("ascii")))
    print("PEER PID : {}".format(binascii.hexlify(peer_pid).decode("ascii")))

    z.close()
