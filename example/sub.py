import argparse
import time
import signal 
import zenoh 
import ctypes
ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenohd", required=True,
                help="ip:port for the zenoh broker")

args = vars(ap.parse_args())

def callback(rname, data, info):    
    print('Received {} bytes of data for resource {} with encoding {}'.format(len(data), rname, info.encoding))
    print(data)
    
    # print('{}'.format(type(data)))    
    # print('{}'.format(type(data.contents)))    

    # print('content type = {}'.format(data.contents))
    # print('content type = {}'.format(data[:(length)]))
    # for i in range(0,length):
    #     print('{}: {:02x}'.format(i, data[i][0]))
    

if __name__ == '__main__':    
    z = zenoh.Zenoh(args['zenohd'], 'user'.encode(), 'password'.encode())
    r_name = '/demo/hello/*'
    
    print('Declaring Subscriber for {}', r_name)
    
    sub = z.declare_subscriber(r_name, zenoh.SubscriberMode.push(), callback)
    time.sleep(60)