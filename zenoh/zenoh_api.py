from .binding import *

class SubscriberMode(object):
  Z_PUSH_MODE = 1
  Z_PULL_MODE = 2
  Z_PERIODIC_PUSH_MODE = 3
  Z_PERIODIC_PULL_MODE = 4


  def __init__(self, kind, tprop):
    self.z_sm = z_sub_mode_t()
    self.z_sm.kind = c_uint8(kind)
    self.z_sm.tprop.origin = 0
    self.z_sm.tprop.period = 0
    self.z_sm.tprop.duration = 0

    if tprop is not None:
        self.z_sm.tprop.origin = tprop.origin
        self.z_sm.tprop.period = tprop.period
        self.z_sm.tprop.duration = tprop.duration


  @staticmethod 
  def push():
    return SubscriberMode(SubscriberMode.Z_PUSH_MODE, None)


class Zenoh(object): 
    zenoh_native_lib = CDLL(zenoh_lib_path)     
    def __init__(self,  locator, uid = None, pwd = None):                                                  
        self.zlib =  Zenoh.zenoh_native_lib        
                
        self.zlib.z_open_wup.restype = z_zenoh_p_result_t
        self.zlib.z_open_wup.argtypes = [c_char_p, c_char_p, c_char_p]

        self.zlib.z_declare_subscriber.restype = z_sub_p_result_t
        self.zlib.z_declare_subscriber.argtypes = [c_void_p, c_char_p, POINTER(z_sub_mode_t), ZENOH_SUBSCRIBER_CALLBACK_PROTO, POINTER(c_int64)]

        self.zlib.z_declare_storage.restype = z_sto_p_result_t
        self.zlib.z_declare_storage.argtypes = [c_void_p, c_char_p, ZENOH_SUBSCRIBER_CALLBACK_PROTO, ZENOH_QUERY_HANDLER_PROTO, ZENOH_REPLY_CLEANER_PROTO, POINTER(c_int64)]
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

        self.zlib.z_query.restype = c_int
        self.zlib.z_query.argtypes = [c_void_p, c_char_p, c_char_p, ZENOH_REPLY_CALLBACK_PROTO, POINTER(c_int64)]

        self.zlib.intersect.restype = c_int 
        self.zlib.intersect.argtypes = [c_char_p, c_char_p]

        self.zenoh = self.zlib.z_open_wup(locator.encode(), uid, pwd).value.zenoh
        
        if self.zenoh != None:
            self.connected = True
        else:
            raise 'Unable to open zenoh session!'

        self.zlib.z_start_recv_loop(self.zenoh)

    @staticmethod
    def intersect( a, b):
        if Zenoh.zenoh_native_lib.intersect(a.encode(), b.encode()) == 1:
            return True
        else: 
            return False

    def declare_publisher(self, res_name):
        r = self.zlib.z_declare_publisher(self.zenoh, res_name.encode())
        if r.tag == 0:
            return r.value.pub
        else:
            raise 'Unable to create publisher'

    def declare_subscriber(self, res_name, sub_mode, callback):        
        global subscriberCallbackMap        
        h = hash(callback)
        k = POINTER(c_int64)()
        k.contents = c_int64()
        k.contents.value = h        
        r = self.zlib.z_declare_subscriber(self.zenoh, res_name.encode(), byref(sub_mode.z_sm), z_subscriber_trampoline_callback, k)
        subscriberCallbackMap[h] = (k, callback)        
        if r.tag == 0:
            return r.value.sub
        else:            
            del subscriberCallbackMap[h]
            raise 'Unable to create subscriber'
        
    def declare_storage(self, resource, subscriber_callback, query_handler):
        global replyCallbackMap
        h = hash(query_handler)
        k = POINTER(c_int64)()
        k.contents = c_int64()
        k.contents.value = h                
        r = self.zlib.z_declare_storage(self.zenoh, resource.encode(), z_subscriber_trampoline_callback, z_query_handler_trampoline, z_no_op_reply_cleaner, k)
        subscriberCallbackMap[h] = (k, subscriber_callback)
        queryHandlerMap[h] = (k, query_handler)
        if r.tag == 0:
            return r.value.sto
        else:
            del subscriberCallbackMap[h]
            del replyCallbackMap[h]            
        
        
    def stream_compact_data(self, pub, data):          
        l = len(data)
        self.zlib.z_stream_compact_data(pub, data, l)

    def stream_data(self, pub, data):             
        l = len(data)
        self.zlib.z_stream_data(pub, data, l)        

    def write_data_wo(self, resource, data, encoding, kind):
        l = len(data)
        self.zlib.z_write_data_wo(self.zenoh, resource.encode(), data, l, encoding, kind)

    def write_data(self, resource, data):
        self.write_data_wo(resource, data, 0, Z_PUT)

    def query(self, resource, predicate, callback):
        global replyCallbackMap        
        h = hash(callback)
        k = POINTER(c_int64)()
        k.contents = c_int64()
        k.contents.value = h        
        r = self.zlib.z_query(self.zenoh, resource.encode(), predicate.encode(), z_reply_trampoline_callback, k)
        replyCallbackMap[h] = (k, callback)        
        if r != 0:            
            del replyCallbackMap[h]
            raise 'Unable to create query'        

      
    def close(self):        
        pass



    