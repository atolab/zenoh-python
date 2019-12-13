import sys
import time
from zenoh.net import (
    Session, QueryDest,
    ZN_STORAGE_DATA, ZN_STORAGE_FINAL,
    ZN_EVAL_DATA, ZN_EVAL_FINAL
)


def reply_handler(reply):
    if reply.kind == ZN_STORAGE_DATA:
        print(">> [Reply handler] received -Storage Data- ('{}': '{}')"
              .format(reply.rname, reply.data.decode("utf-8")))
    elif reply.kind == ZN_EVAL_DATA:
        print(">> [Reply handler] received -Eval Data-    ('{}': '{}')"
              .format(reply.rname, reply.data.decode("utf-8")))
    elif reply.kind == ZN_STORAGE_FINAL:
        print(">> [Reply handler] received -Storage Final-")
    elif reply.kind == ZN_EVAL_FINAL:
        print(">> [Reply handler] received -Eval Final-")
    else:
        print(">> [Reply handler] received -Reply Final-")


if __name__ == '__main__':
    uri = "/demo/example/**"
    if len(sys.argv) > 1:
        uri = sys.argv[1]

    locator = None
    if len(sys.argv) > 2:
        locator = sys.argv[2]

    print("Openning session...")
    s = Session.open(locator)

    print("Sending query '{}'...".format(uri))
    s.query(uri, "", reply_handler,
            dest_storages=QueryDest(QueryDest.ZN_ALL),
            dest_evals=QueryDest(QueryDest.ZN_ALL))

    time.sleep(1)

    s.close()
