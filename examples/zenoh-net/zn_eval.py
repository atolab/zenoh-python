import sys
import time
from zenoh.net import Session, DataInfo, ZN_PUT


def query_handler(path_selector, content_selector, send_replies):
    print(">> [Query handler] Handling '{}?{}'"
          .format(path_selector, content_selector))
    k, v = "/demo/example/zenoh-python-eval", "Eval from Python!".encode()
    send_replies([(k, (v, DataInfo(kind=ZN_PUT)))])


if __name__ == '__main__':
    uri = "/demo/example/zenoh-python-eval"
    if len(sys.argv) > 1:
        uri = sys.argv[1]

    locator = None
    if len(sys.argv) > 2:
        locator = sys.argv[2]

    print("Openning session...")
    s = Session.open(locator)

    print("Declaring Eval on '{}'...".format(uri))
    eva = s.declare_eval(uri, query_handler)

    c = '\0'
    while c != 'q':
        c = sys.stdin.read(1)

    s.undeclare_eval(eva)
    s.close()
