from zenoh.zenoh_api import Zenoh
import logging 

def connect(addr):
    return Zenoh.connect(addr)

