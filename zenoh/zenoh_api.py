from .binding import *

class SubscriberMode(object):
  Z_PUSH_MODE = 0x01
  Z_PULL_MODE = 0x02
  Z_PERIODIC_PUSH_MODE = 0x03
  Z_PERIODIC_PULL_MODE = 0x04


  def __init__(self, kind, tprop):
    self.kind = kind
    self.tprop = tprop
  
  @staticmethod 
  def push():
    return SubscriberMode(Z_PUSH_MODE, z_temporal_property_t(0, 0))


class Zenoh(object):   
    def __init__(self,  locator, uid = None, pwd = None):                                                  
        self.zlib =  CDLL(zenoh_lib_path)
                
        self.zlib.z_open_wup.restype = c_void_p
        self.zlib.z_open_wup.argtypes = [c_char_p, c_char_p, c_char_p]

        self.zlib.z_declare_subscriber.restype = z_sub_p_result_t
        self.zlib.z_declare_subscriber.argtypes = [c_void_p, c_char_p, z_temporal_property_t, ZENOH_SUBSCRIBER_CALLBACK_PROTO]

        self.zlib.z_declare_publisher.restype = z_pub_p_result_t
        self.zlib.z_declare_publisher.argtypes = [c_void_p, c_char_p]

        self.zlib.z_start_recv_loop.restype = c_int
        self.zlib.z_start_recv_loop.argtypes = [c_void_p]

        self.zlib.z_stream_compact_data.restype = c_int 
        self.zlib.z_stream_compact_data.argtypes = [c_void_p, POINTER(c_char), c_int]

        self.zlib.z_stream_data.restype = c_int 
        self.zlib.z_stream_data.argtypes = [c_void_p, c_char_p, c_int]

        self.zlib.z_write_data.restype = c_int 
        self.zlib.z_write_data.argtypes = [c_void_p, c_char_p, c_char_p, c_int]

        self.zlib.z_stream_data_wo.restype = c_int 
        self.zlib.z_stream_data_wo.argtypes = [c_void_p, c_char_p, c_int, c_uint8, c_uint8]

        self.zlib.z_write_data_wo.restype = c_int 
        self.zlib.z_write_data_wo.argtypes = [c_void_p, c_char_p, c_char_p, c_int, c_uint8, c_uint8]

        self.zenoh = self.zlib.z_open_wup(locator.encode(), uid, pwd)
        
        if self.zenoh != None:
            self.connected = True
        else:
            raise 'Unable to open zenoh session!'

        self.zlib.z_start_recv_loop(self.zenoh)

    def declare_publisher(self, res_name):
        r = self.zlib.z_declare_publisher(self.zenoh, res_name.encode())
        if r.tag == 0:
            return r.value.pub
        else:
            raise 'Unable to create publisher'

    def declare_subscriber(self, res_name, sub_mode, callback):
        listener = SubscriberCallback(callback)
        r = self.zlib.z_declare_subscriber(res_name, sub_mode, listener.callback)
        if r.tag == 0:
            return r.value.sub
        else:
            raise 'Unable to create subscriber'

        
    def stream_compact_data(self, pub, data):          
        l = len(data)
        self.zlib.z_stream_compact_data(pub, data, l)

    def stream_data(self, pub, data):             
        l = len(data)
        self.zlib.z_stream_data(pub, data, l)        

    def close(self):        
        pass



    