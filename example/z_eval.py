import sys
import time
import zenoh


def query_handler(path_selector, content_selector, send_replies):
    print(">> [Query handler] Handling '{}?{}'"
          .format(path_selector, content_selector))
    k, v = "/demo/example/zenoh-python-eval", "Eval from Python!".encode()
    send_replies([(k, (v, zenoh.DataInfo(kind=zenoh.Z_PUT)))])


if __name__ == '__main__':
    locator = "tcp/127.0.0.1:7447"
    if len(sys.argv) > 1:
        locator = sys.argv[1]

    uri = "/demo/example/zenoh-python-eval"
    if len(sys.argv) > 2:
        uri = sys.argv[2]

    print("Connecting to {}...".format(locator))
    z = zenoh.Zenoh(locator, 'user', 'password')

    print("Declaring Eval on '{}'...".format(uri))
    eva = z.declare_eval(uri, query_handler)

    while True:
        time.sleep(60)

    z.undeclare_eval(eva)
    z.close()
