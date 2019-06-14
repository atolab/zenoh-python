import zenoh
import argparse
import time
import signal 

ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenohd", required=True,
                help="ip:port for the zenoh broker")

args = vars(ap.parse_args())

def run_pub(locator):        
    z = zenoh.Zenoh(locator, 'user'.encode(), 'password'.encode())    
    r_name = '/test/thr'
    print('Declaring Publisher for {}', r_name)
    pub = z.declare_publisher(r_name)            

    count = 0
    while True:
        msg = '01234567012345670123456701234567'.encode()
        z.stream_data(pub, msg)        
        

    z.close()

if __name__ == '__main__':    
    run_pub(args['zenohd'])


