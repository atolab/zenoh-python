import argparse
import time
import signal 
import zenoh 

ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenohd", required=True,
                help="ip:port for the zenoh broker")

args = vars(ap.parse_args())


def callback(reply):  
  if reply.kind == zenoh.QueryReply.STORAGE_DATA:
    print('Received: ({}, {}) '.format(reply.rname, reply.data))
    
  elif reply.kind == zenoh.Z_STORAGE_FINAL:
    print('Received storage final')
  else:
    print('Received Reply final')
    

if __name__ == '__main__':    
    z = zenoh.Zenoh(args['zenohd'], 'user'.encode(), 'password'.encode())
    selector = '/demo/**'
    
    print('Execuring query {}', selector)
    
    while True:
      z.query(selector, "", callback)
      time.sleep(1)
    