from zenoh import Zenoh, SubscriberMode
import time
import sys


def listener(rname, data, info):
    print("{}: {}".format(rname, data.decode()))


if __name__ == "__main__":
    locator = None
    if len(sys.argv) > 1:
        locator = sys.argv[1]

    z = Zenoh.open(locator)
    sub = z.declare_subscriber('/myhome/kitcken/temp',
                               SubscriberMode.push(),
                               listener)

    # Listen for one minute and then exit
    time.sleep(120)
    z.undeclare_subscriber(sub)
    z.close()
