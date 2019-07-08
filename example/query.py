import argparse
import time
import signal 
import zenoh 

ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenohd", required=True,
                help="ip:port for the zenoh broker")

args = vars(ap.parse_args())


def callback(data):
  if data.kind == zenoh.Z_STORAGE_DATA:
    print('Received data for resource: {}'.format(data.rname.decode()))
  elif data.kind == zenoh.Z_STORAGE_FINAL:
    print('Received storage final')
  else:
    print('Received Reply final')
    exit(0)

if __name__ == '__main__':    
    z = zenoh.Zenoh(args['zenohd'], 'user'.encode(), 'password'.encode())
    selector = '/demo/**'
    
    print('Execuring query {}', selector)
    
    sub = z.query(selector, "", callback)
    time.sleep(60)