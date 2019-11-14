import sys
import time
import itertools
from zenoh import Zenoh


if __name__ == '__main__':
    uri = "/demo/example/zenoh-python-stream"
    if len(sys.argv) > 1:
        uri = sys.argv[1]

    value = "Stream from Python!"
    if len(sys.argv) > 2:
        value = sys.argv[2]

    locator = None
    if len(sys.argv) > 3:
        locator = sys.argv[3]

    print("Openning session...")
    z = Zenoh.open(locator)

    print("Declaring Publisher on '{}'...".format(uri))
    pub = z.declare_publisher(uri)

    for idx in itertools.count():
        time.sleep(1)
        buf = "[{:4d}] {}".format(idx, value)
        print("Streaming Data ('{}': '{}')...".format(uri, buf))
        z.stream_data(pub, bytes(buf, encoding='utf8'))

    z.undeclare_publisher(pub)
    z.close()
