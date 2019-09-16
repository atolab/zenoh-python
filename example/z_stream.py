import sys
import time
import itertools
import zenoh


if __name__ == '__main__':
    locator = "tcp/127.0.0.1:7447"
    if len(sys.argv) > 1:
        locator = sys.argv[1]

    uri = "/demo/example/zenoh-python-stream"
    if len(sys.argv) > 2:
        uri = sys.argv[2]

    value = "Stream from Python!"
    if len(sys.argv) > 3:
        value = sys.argv[3]

    print("Connecting to {}...".format(locator))
    z = zenoh.Zenoh(locator, 'user', 'password')

    print("Declaring Publisher on '{}'".format(uri))
    pub = z.declare_publisher(uri)

    for idx in itertools.count():
        time.sleep(1)
        buf = "[{:4d}] {}".format(idx, value)
        print("Streaming Data ('{}': '{}')...".format(uri, buf))
        z.stream_data(pub, bytes(buf, encoding='utf8'))

    z.undeclare_publisher(pub)
    z.close()
