import argparse
import zenoh 

ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenohd", required=True,
                help="ip:port for the zenoh broker")

ap.add_argument("-l", "--log", required=False,
                help="Log level (INFO, DEBUG, WARNING, ERROR, CRITICAL)")
args = vars(ap.parse_args())

def sub_callback(rid, data):
    print('Received \'{}\' for resource {}'.format(data.tobytes().decode('utf-8'), rid))

def run_sub(broker):        
    z = zenoh.connect(broker)   
    print('Declaring Subscriber')
    rname = '//demo/hello'
    rid = z.declare_subscriber(rname, sub_callback)    
    print('Declared subscriber for {}:{}'.format(rname, rid))


if __name__ == '__main__':    
    run_sub(args['zenohd'])


