import sys
import time
from zenoh import Zenoh, DataInfo, Z_PUT


def query_handler(path_selector, content_selector, send_replies):
    print(">> [Query handler] Handling '{}?{}'"
          .format(path_selector, content_selector))
    k, v = "/demo/example/zenoh-python-eval", "Eval from Python!".encode()
    send_replies([(k, (v, DataInfo(kind=Z_PUT)))])


if __name__ == '__main__':
    uri = "/demo/example/zenoh-python-eval"
    if len(sys.argv) > 1:
        uri = sys.argv[1]

    locator = None
    if len(sys.argv) > 2:
        locator = sys.argv[2]

    print("Openning session...")
    z = Zenoh.open(locator)

    print("Declaring Eval on '{}'...".format(uri))
    eva = z.declare_eval(uri, query_handler)

    c = '\0'
    while c != 'q':
        c = sys.stdin.read(1)

    z.undeclare_eval(eva)
    z.close()
