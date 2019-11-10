import sys
import time
from zenoh import Zenoh


if __name__ == '__main__':
    locator = None
    if len(sys.argv) > 1:
        locator = sys.argv[1]

    uri = "/demo/example/zenoh-python-write"
    if len(sys.argv) > 2:
        uri = sys.argv[2]

    value = "Write from Python!"
    if len(sys.argv) > 3:
        value = sys.argv[3]

    print("Openning session...")
    z = Zenoh.open(locator)

    print("Writing Data ('{}': '{}')...".format(uri, value))
    z.write_data(uri, bytes(value, encoding='utf8'))

    z.close()
