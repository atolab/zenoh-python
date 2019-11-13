from zenoh import Zenoh, SubscriberMode
import time

def listener(rname, data, info):
    print("{}: {}".format(rname, data.decode()))
    

if __name__ == "__main__":        
    z = Zenoh.open()
    sub = z.declare_subscriber('/myhome/kitcken/temp', SubscriberMode.push(), listener)
    
    # Listen for one minute and then exit
    time.sleep(10)
    z.undeclare_subscriber(sub)
    z.close()