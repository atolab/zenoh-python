import argparse
import time
import signal 
import zenoh 

ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenohd", required=True,
                help="ip:port for the zenoh broker")

args = vars(ap.parse_args())

store =  {}

def insert_handler(rname, data, length, info):
  print('Inserting data for resource: {}'.format(rname))
  store[rname] = (data, length, info)

def query_handler(path_selector, content_selector):  
  return []

if __name__ == '__main__':    
    z = zenoh.Zenoh(args['zenohd'], 'user'.encode(), 'password'.encode())
    r_name = '/demo/hello/*'
    
    print('Declaring Subscriber for {}', r_name)
    
    sub = z.declare_storage(r_name, insert_handler, query_handler)
    time.sleep(600)