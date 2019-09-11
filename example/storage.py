import argparse
import time
import signal
import zenoh

ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenohd", required=True,
                help="ip:port for the zenoh broker")
args = vars(ap.parse_args())

store = {}


def insert_handler(rname, data, info):
    print('Inserting data for resource: {}'.format(rname))
    store[rname] = (data, info)


def query_handler(path_selector, content_selector, send_replies):
    replies = []
    for k, v in store.items():
        if zenoh.Zenoh.intersect(path_selector, k):
            print('Responding to query with ({}, {})'.format(k, v))
            replies.append((k, v))
    send_replies(replies)


if __name__ == '__main__':
    z = zenoh.Zenoh(args['zenohd'], 'user', 'password')
    r_name = '/demo/hello/*'

    print('Declaring Storage for {}', r_name)
    sto = z.declare_storage(r_name, insert_handler, query_handler)

    time.sleep(600)

    z.undeclare_storage(sto)
