import sys
import time
import datetime
from zenoh import Zenoh, SubscriberMode

N = 100000

count = 0
start = None
stop = None


def print_stats(start, stop):
    print("{:.6f} msgs/sec".format(N / (stop - start).total_seconds()))


def listener(rname, data, info):
    global count, start, stop
    if count == 0:
        start = datetime.datetime.now()
        count += 1
    elif count < N:
        count += 1
    else:
        stop = datetime.datetime.now()
        print_stats(start, stop)
        count = 0


if __name__ == '__main__':
    locator = "tcp/127.0.0.1:7447"
    if len(sys.argv) > 1:
        locator = sys.argv[1]

    z = Zenoh.open(locator)
    sub = z.declare_subscriber('/test/thr', SubscriberMode.push(), listener)

    time.sleep(60)

    z.undeclare_subscriber(sub)
    z.close()
