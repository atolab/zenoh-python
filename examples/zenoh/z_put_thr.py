import time
import sys
from zenoh import Zenoh, Selector, Path, Workspace, Encoding, Value
import argparse

locator = None
if len(sys.argv) < 2:
    print('USAGE:\n\tz_put_thr <payload-size> [<zenoh-locator>]\n\n')
    sys.exit(-1)

length = int(sys.argv[1])
print("Running throughput test for payload of {} bytes".format(length))
if len(sys.argv) > 2:
    locator = sys.argv[2]

path = '/test/thr'

data = bytearray()
for i in range(0, length):
    data.append(i % 10)
v = Value(data, encoding=Encoding.RAW)

print('Login to Zenoh...')
z = Zenoh.login(locator)
print("Use Workspace on '/'")
w = z.workspace('/')

while True:
    w.put(path, v)
