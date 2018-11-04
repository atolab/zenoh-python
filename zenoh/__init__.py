from zenoh.zenoh_api import Zenoh

def connect(addr):
    return Zenoh.connect(addr)