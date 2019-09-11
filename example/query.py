import argparse
import time
import signal
import zenoh

ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenohd", required=True,
                help="ip:port for the zenoh broker")

args = vars(ap.parse_args())


def callback(reply):
    if reply.kind == zenoh.Z_STORAGE_DATA:
        print('Received Storage Data: ({}, {}) '
              .format(reply.rname, reply.data))
    if reply.kind == zenoh.Z_EVAL_DATA:
        print('Received Eval Data: ({}, {}) '
              .format(reply.rname, reply.data))
    elif reply.kind == zenoh.Z_STORAGE_FINAL:
        print('Received Storage Final')
    elif reply.kind == zenoh.Z_EVAL_FINAL:
        print('Received Eval Final')
    else:
        print('Received Reply Final')


if __name__ == '__main__':
    z = zenoh.Zenoh(args['zenohd'], 'user', 'password')
    selector = '/demo/**'

    print('Execuring query {}', selector)
    z.query(selector, "", callback)

    time.sleep(2)
