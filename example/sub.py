import argparse
import time
import signal 
import zenoh 

ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenohd", required=True,
                help="ip:port for the zenoh broker")

args = vars(ap.parse_args())

def callback(rname, data, length, info):
    print('Received {} bytes of data for resource {} with encoding {}'.format(length, rname, info.encoding))

if __name__ == '__main__':    
    z = zenoh.Zenoh(args['zenohd'], 'user'.encode(), 'password'.encode())
    r_name = '/demo/hello/*'
    
    print('Declaring Subscriber for {}', r_name)
    
    sub = z.declare_subscriber(r_name, zenoh.SubscriberMode.push(), callback)
    time.sleep(60)