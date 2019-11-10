import sys
import time
from zenoh import Zenoh, SubscriberMode


def listener(rname, data, info):
    print(">> [Subscription listener] Received ('{}': '{}')"
          .format(rname, data.decode("utf-8")))


if __name__ == '__main__':
    locator = None
    if len(sys.argv) > 1:
        locator = sys.argv[1]

    uri = "/demo/example/**"
    if len(sys.argv) > 2:
        uri = sys.argv[2]

    print("Openning session...")
    z = Zenoh.open(locator)

    print("Declaring Subscriber on '{}'...".format(uri))
    sub = z.declare_subscriber(uri, SubscriberMode.pull(), listener)

    print("Press <enter> to pull data...");
    c = '\0'
    while c != 'q':
        c = sys.stdin.read(1)
        z.pull(sub)

    z.undeclare_subscriber(sub)
    z.close()
