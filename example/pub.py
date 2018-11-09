import zenoh
import argparse
import time
import signal 

ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenohd", required=True,
                help="ip:port for the zenoh broker")
ap.add_argument("-l", "--log", required=False,
                help="Log level (INFO, DEBUG, WARNING, ERROR, CRITICAL)")

args = vars(ap.parse_args())

def matching_observer(b):
    print('Publisher Matching: {}'.format(b))

def run_pub(broker):        
    z = zenoh.connect(broker)   
    print('Declaring Publisher')
    pub = z.declare_publisher('//demo/hello')
    print('Declared Publisher on resource {}:{}'.format(pub.rname, pub.rid))
    pub.observe_matching(matching_observer)
    count = 0
    for _ in range(1, 30):
        pub.write('[{}]: Hello to the Zenoh World'.format(count).encode())
        count += 1
        time.sleep(0.5)

    z.close()

if __name__ == '__main__':    
    run_pub(args['zenohd'])


