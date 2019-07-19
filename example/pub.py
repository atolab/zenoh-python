import zenoh
import argparse
import time
import signal 

ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenohd", required=True,
                help="ip:port for the zenoh broker")

args = vars(ap.parse_args())

def run_pub(locator):        
    z = zenoh.Zenoh(locator, 'user', 'password')
    r_name = '/demo/hello/piton'
    print('Declaring Publisher for {}', r_name)
    pub = z.declare_publisher(r_name)            

    count = 0
    for _ in range(1, 30):
        print('Sending data...')
        msg = 'Salut des pitone'
        bs = bytearray()
        bs.append(len(msg))
        bs.extend(msg.encode())
        z.stream_data(pub, bytes(bs))
        z.write_data('/demo/hello/ruby', bytes(bs))
        z.write_data('/demo/hello/ruby', bytes(bs))
        count += 1
        time.sleep(0.5)

    z.close()

if __name__ == '__main__':    
    run_pub(args['zenohd'])


