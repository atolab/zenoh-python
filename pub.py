import zenoh
import argparse
import time

ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenohd", required=True,
                help="ip:port for the zenoh broker")

args = vars(ap.parse_args())

def matching_observer(b):
    print('Publisher Matching: {}'.format(b))

def run_pub(broker):        
    z = zenoh.connect(broker)   
    print('Declaring Publisher')
    pub = z.declare_publisher('//demo/hello')
    print('Declared Publisher on resource {}:{}'.format(pub.rname, pub.rid))
    pub.observe_matching(matching_observer)
    while True:
        pub.write('Hello to the Zenoh World'.encode())
        time.sleep(1)

if __name__ == '__main__':    
    run_pub(args['zenohd'])


