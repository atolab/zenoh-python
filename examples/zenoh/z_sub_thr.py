import sys
import time
import datetime
from zenoh import Zenoh, Selector, Path, Workspace, Encoding, Value

N = 100000

count = 0
start = None
stop = None


def print_stats(start, stop):
    print("{:.6f} msgs/sec".format(N / (stop - start).total_seconds()))


def listener(changes):
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


locator = None
if len(sys.argv) > 1:
    locator = sys.argv[1]

selector = '/test/thr'

print('Login to Zenoh (locator={})...'.format(locator))
z = Zenoh.login(locator)

print("Use Workspace on '/'")
w = z.workspace('/')

print("Subscribe on {}".format(selector))
subid = w.subscribe(selector, listener)

time.sleep(60)

w.unsubscribe(subid)
z.logout()
