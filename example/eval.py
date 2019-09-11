import argparse
import time
import signal
import zenoh

ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenohd", required=True,
                help="ip:port for the zenoh broker")
args = vars(ap.parse_args())


def query_handler(path_selector, content_selector, send_replies):
    k, v = "/demo/hello/eval", "EVAL_DATA".encode()
    print('Responding to query with ({}, {})'.format(k, v))
    send_replies([(k, (v, zenoh.DataInfo(kind=zenoh.Z_PUT)))])


if __name__ == '__main__':
    z = zenoh.Zenoh(args['zenohd'], 'user', 'password')
    r_name = '/demo/hello/eval'

    print('Declaring Eval for {}', r_name)
    eva = z.declare_eval(r_name, query_handler)

    time.sleep(600)

    z.undeclare_eval(eva)
