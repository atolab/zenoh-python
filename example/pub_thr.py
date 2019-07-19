import zenoh
import argparse
import time
import signal 

ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenohd", required=True,
                help="ip:port for the zenoh broker")
ap.add_argument("-s", "--size", required=True,
                help="payload size")

args = vars(ap.parse_args())

def run_pub(locator):        
    z = zenoh.Zenoh(locator, 'user', 'password')
    r_name = '/test/thr'
    print('Declaring Publisher for {}', r_name)
    pub = z.declare_publisher(r_name)            

    count = 0
    size = int(args['size'])    
    bs = bytearray()
    for i in range(0,size):
        bs.append(i % 256)

    while True:        
        z.stream_data(pub, bytes(bs))        
        

    z.close()

if __name__ == '__main__':    
    run_pub(args['zenohd'])


