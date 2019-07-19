import argparse
import time
import signal 
import zenoh 

ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenohd", required=True,
                help="ip:port for the zenoh broker")

args = vars(ap.parse_args())

store =  {}

def insert_handler(rname, data, info):
  print('Inserting data for resource: {}'.format(rname))
  store[rname] = (data, info)

def query_handler(path_selector, content_selector):  
  reply = []
  for k,v in store.items():
    if zenoh.Zenoh.intersect(path_selector, k):
      print('Responding to query with ({}, {})'.format(k, v))
      reply.append((k,v))
  return reply

if __name__ == '__main__':    
    z = zenoh.Zenoh(args['zenohd'], 'user', 'password')
    r_name = '/demo/hello/*'
    
    print('Declaring Subscriber for {}', r_name)
    
    sub = z.declare_storage(r_name, insert_handler, query_handler)
    time.sleep(600)