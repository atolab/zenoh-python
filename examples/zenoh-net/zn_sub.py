import sys
import time
from zenoh.net import Session, SubscriberMode


def listener(rname, data, info):
    print(">> [Subscription listener] Received ('{}': '{}') at {}"
          .format(rname, data.decode("utf-8"), info.tstamp))


if __name__ == '__main__':
    uri = "/demo/example/**"
    if len(sys.argv) > 1:
        uri = sys.argv[1]

    locator = None
    if len(sys.argv) > 2:
        locator = sys.argv[2]

    print("Openning session...")
    s = Session.open(locator)

    print("Declaring Subscriber on '{}'...".format(uri))
    sub = s.declare_subscriber(uri, SubscriberMode.push(), listener)

    c = '\0'
    while c != 'q':
        c = sys.stdin.read(1)

    s.undeclare_subscriber(sub)
    s.close()
