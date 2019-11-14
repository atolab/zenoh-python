import sys
import time
from zenoh import Zenoh

store = {}


def listener(rname, data, info):
    print(">> [Storage listener] Received ('{}': '{}')"
          .format(rname, data.decode("utf-8")))
    store[rname] = (data, info)


def query_handler(path_selector, content_selector, send_replies):
    print(">> [Query handler   ] Handling '{}?{}'"
          .format(path_selector, content_selector))
    replies = []
    for k, v in store.items():
        if Zenoh.intersect(path_selector, k):
            replies.append((k, v))
    send_replies(replies)


if __name__ == '__main__':
    uri = "/demo/example/**"
    if len(sys.argv) > 1:
        uri = sys.argv[1]

    locator = None
    if len(sys.argv) > 2:
        locator = sys.argv[2]

    print("Openning session...")
    z = Zenoh.open(locator)

    print("Declaring Storage on '{}'...".format(uri))
    sto = z.declare_storage(uri, listener, query_handler)

    c = '\0'
    while c != 'q':
        c = sys.stdin.read(1)

    z.undeclare_storage(sto)
    z.close()
