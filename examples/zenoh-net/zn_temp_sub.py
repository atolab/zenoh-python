from zenoh.net import Session, SubscriberMode
import time
import sys


def listener(rname, data, info):
    print("{}: {}".format(rname, data.decode()))


if __name__ == "__main__":
    locator = None
    if len(sys.argv) > 1:
        locator = sys.argv[1]

    s = Session.open(locator)
    sub = s.declare_subscriber('/myhome/kitcken/temp',
                               SubscriberMode.push(),
                               listener)

    # Listen for one minute and then exit
    time.sleep(120)
    s.undeclare_subscriber(sub)
    s.close()
