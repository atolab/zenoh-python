from .binding import *
import socket


Z_INFO_PID_KEY      = 0
Z_INFO_PEER_KEY     = 1
Z_INFO_PEER_PID_KEY = 2

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

def z_to_canonical_locator(locator):
    locator = locator.strip()
    a, b, c = locator.partition('/')
    if a == 'tcp' and b == '/':
        h, s, p = c.partition(':')
        if s == ':' and p != '':
            return 'tcp/' + socket.gethostbyname(h) + ':' + p
        else:
            raise Exception('Invalid locator format {}, it should be tcp/<ip-addr|host-name>:port'.format(locator))
    elif b == '':
        h, s, p = locator.partition(':')
        if s == ':':
            return 'tcp/' + socket.gethostbyname(h) + ':' + p
        else:
            return 'tcp/' + socket.gethostbyname(h) + ':' + str(7447)

class Zenoh(object): 
    zenoh_native_lib = CDLL(zenoh_lib_path)
    
    
    def __init__(self,  locator, uid = None, pwd = None):                                                  
        """
            Creates a zenoh runtimes and connect to the broker specified by the locator using
            the optional user-id and password.

            :param locator: the zenoh broker locator
            :param uid: the optional user id
            :param pwd: the optional user password
        """
        assert(Zenoh.zenoh_native_lib is not None)

        self.zlib =  Zenoh.zenoh_native_lib                

        self.zlib.z_open_wup.restype = z_zenoh_p_result_t
        self.zlib.z_open_wup.argtypes = [c_char_p, c_char_p, c_char_p]

        self.zlib.z_info.restype = z_vec_t
        self.zlib.z_info.argtypes = [c_void_p]

        self.zlib.z_running.restype = c_int
        self.zlib.z_running.argtypes = [c_void_p]

        self.zlib.z_vec_get.restype = c_void_p
        self.zlib.z_vec_get.argtypes = [POINTER(z_vec_t), c_uint]

        self.zlib.z_declare_subscriber.restype = z_sub_p_result_t
        self.zlib.z_declare_subscriber.argtypes = [c_void_p, c_char_p, POINTER(z_sub_mode_t), ZENOH_SUBSCRIBER_CALLBACK_PROTO, POINTER(c_int64)]

        self.zlib.z_declare_storage.restype = z_sto_p_result_t
        self.zlib.z_declare_storage.argtypes = [c_void_p, c_char_p, ZENOH_SUBSCRIBER_CALLBACK_PROTO, ZENOH_QUERY_HANDLER_PROTO, ZENOH_REPLY_CLEANER_PROTO, POINTER(c_int64)]
        self.zlib.z_declare_publisher.restype = z_pub_p_result_t
        self.zlib.z_declare_publisher.argtypes = [c_void_p, c_char_p]

        self.zlib.z_start_recv_loop.restype = c_int
        self.zlib.z_start_recv_loop.argtypes = [c_void_p]

        self.zlib.z_stop_recv_loop.restype = c_int
        self.zlib.z_stop_recv_loop.argtypes = [c_void_p]

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

        self.zlib.z_undeclare_subscriber.restype = c_int 
        self.zlib.z_undeclare_subscriber.argtypes = [c_void_p]

        self.zlib.z_undeclare_storage.restype = c_int 
        self.zlib.z_undeclare_storage.argtypes = [c_void_p]

        self.zlib.z_undeclare_publisher.restype = c_int 
        self.zlib.z_undeclare_publisher.argtypes = [c_void_p]

        self.zlib.intersect.restype = c_int 
        self.zlib.intersect.argtypes = [c_char_p, c_char_p]

        l = z_to_canonical_locator(locator)

        r = self.zlib.z_open_wup(l.encode(), uid, pwd)
        if r.tag == Z_OK_TAG:
            self.zenoh = r.value.zenoh
            self.connected = True
        else:        
            raise Exception('Unable to open zenoh session (error code: {}).'.format(r.value.error))

        self.zlib.z_start_recv_loop(self.zenoh)

    def info(self):
        ps = self.zlib.z_info(self.zenoh)
        res = {}
        for i in range(0, ps.length_):
            prop = cast(self.zlib.z_vec_get(pointer(ps), i), POINTER(z_property_t))
            val = prop[0].value
            res[i] = val.elem[:val.length]
        return res
    
    @property
    def running(self):
        return (self.zlib.z_running(self.zenoh) != 0)

    @staticmethod
    def intersect( a, b):
        if Zenoh.zenoh_native_lib.intersect(a.encode(), b.encode()) == 1:
            return True
        else: 
            return False

    def declare_publisher(self, res_name):
        """
            Declares a publisher for a given resource.

            :param res_name: the resource for which the publisher should be declared
            :return: the publisher handle if successful.
        """
        r = self.zlib.z_declare_publisher(self.zenoh, res_name.encode())
        if r.tag == 0:
            return r.value.pub
        else:
            raise Exception('Unable to create publisher')

    def declare_subscriber(self, res_name, sub_mode, callback):        
        """
            Declares a subscriber for a given resource.

            :param res_name: the resource for which the subscriber should be declared
            :return: the subscriber handle if successful.
        """
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
            raise Exception('Unable to create subscriber')
        
    def declare_storage(self, selector, subscriber_callback, query_handler):
        """
            Declares a storage for a given selector.

            :param selector: the resource selector used to specify the keys 
                             that will be stored in this storage
            :subscriber_callback: a callback invoked each time data has to be 
                             inserted in this storage
            :query_handler: a callback called each time a query has to be answered
            :return: a handle to the created storage
        """
        global replyCallbackMap
        h = hash(query_handler)
        k = POINTER(c_int64)()
        k.contents = c_int64()
        k.contents.value = h                
        subscriberCallbackMap[h] = (k, subscriber_callback)
        queryHandlerMap[h] = (k, query_handler)
        r = self.zlib.z_declare_storage(
            self.zenoh, 
            selector.encode(), 
            z_subscriber_trampoline_callback, 
            z_query_handler_trampoline, 
            z_no_op_reply_cleaner, 
            k)
        if r.tag == 0:
            return r.value.sto
        else:
            del subscriberCallbackMap[h]
            del replyCallbackMap[h]    
            raise Exception('Unable to create storage')       
             
        
        
    def stream_compact_data(self, pub, data):   
        """
            Stream data using the most compact message kind. In this case the timestamp 
            or the encoding are not avaialble.

            :param pub: the publisher
            :param data: the bytes containing the data to stream.
        """       
        l = len(data)
        self.zlib.z_stream_compact_data(pub, data, l)

    def stream_data(self, pub, data):             
        """
            Streams data.            

            :param pub: the publisher
            :param data: the bytes containing the data to stream.
        """       
        l = len(data)
        self.zlib.z_stream_data(pub, data, l)        

    def write_data_wo(self, resource, data, encoding, kind):
        """
            Writes data for a given resource withouth requiring the declaration of
            a publisher. This operation should be used for resources that are 
            sporadically written.

            :param resource: the name of the resource
            :param data: the bytes containing the data to stream
            :param encoding: the encoding for the resource
            :param kind: the kind of update
        """       
        l = len(data)
        self.zlib.z_write_data_wo(self.zenoh, resource.encode(), data, l, encoding, kind)

    def write_data(self, resource, data):
        """
            Writes data for a given resource withouth requiring the declaration of
            a publisher. This operation should be used for resources that are 
            sporadically written.

            :param resource: the name of the resource
            :param data: the bytes containing the data to stream
        """
        self.write_data_wo(resource, data, 0, Z_PUT)

    def query(self, resource, predicate, callback):
        """
            Execute a query for a resource selector with a given predicate.

            :param resource: the resource selector
            :param predicate: the predicate
            :param callback: the callback to call when replies to this query are available
        """
        global replyCallbackMap        
        h = hash(callback)
        k = POINTER(c_int64)()
        k.contents = c_int64()
        k.contents.value = h        
        replyCallbackMap[h] = (k, callback)        
        r = self.zlib.z_query(self.zenoh, resource.encode(), predicate.encode(), z_reply_trampoline_callback, k)
        if r != 0:            
            del replyCallbackMap[h]
            raise Exception('Unable to create query')

    def undeclare_publisher(self, pub):
        self.zlib.z_undeclare_publisher(pub)

    def undeclare_subscriber(self, sub):
        self.zlib.z_undeclare_subscriber(sub)

    def undeclare_storage(self, sto):
        self.zlib.z_undeclare_storage(sto)

    def close(self):        
        """
            Closes the zenoh session.
        """
        self.zlib.z_stop_recv_loop(self.zenoh)



    