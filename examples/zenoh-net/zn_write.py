import sys
import time
from zenoh.net import Session


if __name__ == '__main__':
    uri = "/demo/example/zenoh-python-write"
    if len(sys.argv) > 1:
        uri = sys.argv[1]

    value = "Write from Python!"
    if len(sys.argv) > 2:
        value = sys.argv[2]

    locator = None
    if len(sys.argv) > 3:
        locator = sys.argv[3]

    print("Openning session...")
    s = Session.open(locator)

    print("Writing Data ('{}': '{}')...".format(uri, value))
    s.write_data(uri, bytes(value, encoding='utf8'))

    s.close()
