import sys
import time
import itertools
from zenoh.net import Session


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
    s = Session.open(locator)

    print("Declaring Publisher on '{}'...".format(uri))
    pub = s.declare_publisher(uri)

    for idx in itertools.count():
        time.sleep(1)
        buf = "[{:4d}] {}".format(idx, value)
        print("Streaming Data ('{}': '{}')...".format(uri, buf))
        s.stream_data(pub, bytes(buf, encoding='utf8'))

    s.undeclare_publisher(pub)
    s.close()
