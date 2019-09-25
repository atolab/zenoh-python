import sys
import time
import zenoh
from zenoh import QueryDest


def reply_handler(reply):
    if reply.kind == zenoh.Z_STORAGE_DATA:
        print(">> [Reply handler] received -Storage Data- ('{}': '{}')"
              .format(reply.rname, reply.data.decode("utf-8")))
    elif reply.kind == zenoh.Z_EVAL_DATA:
        print(">> [Reply handler] received -Eval Data-    ('{}': '{}')"
              .format(reply.rname, reply.data.decode("utf-8")))
    elif reply.kind == zenoh.Z_STORAGE_FINAL:
        print(">> [Reply handler] received -Storage Final-")
    elif reply.kind == zenoh.Z_EVAL_FINAL:
        print(">> [Reply handler] received -Eval Final-")
    else:
        print(">> [Reply handler] received -Reply Final-")


if __name__ == '__main__':
    locator = "tcp/127.0.0.1:7447"
    if len(sys.argv) > 1:
        locator = sys.argv[1]

    uri = "/demo/example/**"
    if len(sys.argv) > 2:
        uri = sys.argv[2]

    print("Connecting to {}...".format(locator))
    z = zenoh.Zenoh(locator, 'user', 'password')

    print("Sending query '{}'...".format(uri))
    dest_all = QueryDest(QueryDest.Z_ALL)
    z.query(uri, "", reply_handler,
            dest_storages=dest_all,
            dest_evals=dest_all)

    time.sleep(1)

    z.close()