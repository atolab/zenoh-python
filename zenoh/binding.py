import platform
import os
from ctypes import *


Z_INT_RES_ID = 0
Z_STR_RES_ID = 1


Z_PUT       = 0x00
Z_UPDATE    = 0x01
Z_REMOVE    = 0x02

Z_STORAGE_DATA = 0x00
Z_STORAGE_FINAL = 0x01 
Z_REPLY_FINAL = 0x02 

Z_OK_TAG = 0
Z_ERROR_TAG = 1

subscriberCallbackMap = {}
replyCallbackMap = {}
queryHandlerMap = {}
replyMap = {}

def get_lib_ext():
    system = platform.system()
    if system == 'Linux':
        return '.so'
    elif system == 'Darwin':
        return '.dylib'
    else:
        return '.dll'

def get_user_lib_path():
    system = platform.system()
    if system == 'Linux':
        return '/usr/local/lib'
    elif system == 'Darwin':
        return '/usr/local/lib'
    elif system in ['windows', 'Windows', 'win32']:
        return os.environ['ZENOH_HOME']
    else:
        return '/usr/local/lib'



system = platform.system()
if system in ['windows', 'Windows', 'win32']:
    zenoh_lib = 'zenohc' + get_lib_ext()
    zenoh_lib_path = get_user_lib_path() + os.sep + zenoh_lib    
else:
    zenoh_lib = 'libzenohc' + get_lib_ext()    
    zenoh_lib_path = get_user_lib_path() + os.sep + zenoh_lib


# zenoh-c result types

class z_zenoh_p_result_union_t(Union):
  _fields_ = [('zenoh', c_void_p), ('error', c_int)]

class z_zenoh_p_result_t(Structure):
  _fields_ = [('tag', c_int), ('value', z_zenoh_p_result_union_t)]

class z_pub_p_result_union_t(Union):
  _fields_ = [('pub', c_void_p), ('error', c_int)]

class z_pub_p_result_t(Structure):
  _fields_ = [('tag', c_int), ('value', z_pub_p_result_union_t)]

class z_sub_p_result_union_t(Union):
  _fields_ = [('sub', c_void_p), ('error', c_int)]

class z_sub_p_result_t(Structure):
  _fields_ = [('tag', c_int), ('value', z_sub_p_result_union_t)]

class z_sto_p_result_union_t(Union):
  _fields_ = [('sto', c_void_p), ('error', c_int)]

class z_sto_p_result_t(Structure):
  _fields_ = [('tag', c_int), ('value', z_sto_p_result_union_t)]

class z_vec_t(Structure):
  _fields_ = [('capacity_', c_int), ('length_', c_int), ('elem_', c_void_p)]

# Resource Id
class z_res_id_t(Union):
  _fields_ = [('rid', c_int), ('rname', c_char_p)]

class z_resource_id_t(Structure):
  _fields_ = [('kind', c_int), ('id', z_res_id_t)]

# Data Info
class z_data_info_t(Structure):
  _fields_ = [('flags', c_uint),
              ('encoding', c_ushort),
              ('kind', c_ushort)]

# Temporal properties  
class z_temporal_property_t(Structure):
    _fields_ = [('origin', c_int), ('period', c_int),('duration', c_int)] 

class z_sub_mode_t(Structure):
  _fields_ = [('kind', c_uint8), ('tprop', z_temporal_property_t)]

# properties  
class z_array_uint8_t(Structure):
  _fields_ = [
    ('length', c_uint),
    ('elem', POINTER(c_char))]

class z_property_t(Structure):
  _fields_ = [('id', c_size_t), ('value', z_array_uint8_t)]

CHAR_PTR = POINTER(c_char)
# zenoh-c callbacks
class z_reply_value_t(Structure):
  _fields_ = [
    ('kind', c_uint8), 
    ('stoid', CHAR_PTR),
    ('stoid_length', c_size_t),
    ('rsn', c_uint32), 
    ('rname', c_char_p),
    ('data', CHAR_PTR),
    ('data_length', c_size_t),
    ('info', z_data_info_t)]

class QueryReply(object):
  STORAGE_DATA = 0x00
  STORAGE_FINAL = 0x01 
  REPLY_FINAL = 0x02 

  def __init__(self, zrv):    
    self.kind = zrv.kind
    self.store_id = None
    self.rname = None
    self.data = None
    self.info = None
    
    if self.kind == QueryReply.STORAGE_DATA:
      self.store_id = zrv.stoid[:zrv.stoid_length]
      self.rname = zrv.rname.decode()
      self.data = zrv.data[:zrv.data_length]
      self.info = zrv.info

    elif self.kind == QueryReply.STORAGE_FINAL:
      self.store_id = zrv.stoid[:zrv.stoid_length]
    
    

class z_resource_t(Structure):
  _fields_ = [
    ('rname', c_char_p),
    ('data', CHAR_PTR),
    ('length', c_size_t),
    ('encoding', c_ushort),
    ('kind', c_ushort)
  ]

class z_array_resource_t(Structure):  
  _fields_ = [
    ('length', c_uint),
    ('elem', POINTER(POINTER(z_resource_t)))]
    

ZENOH_ON_DISCONNECT_CALLBACK_PROTO = CFUNCTYPE(None, c_void_p)
ZENOH_SUBSCRIBER_CALLBACK_PROTO = CFUNCTYPE(None, POINTER(z_resource_id_t), CHAR_PTR, c_uint, POINTER(z_data_info_t), POINTER(c_int64))
ZENOH_REPLY_CALLBACK_PROTO = CFUNCTYPE(None, POINTER(z_reply_value_t), POINTER(c_int64))
ZENOH_REPLY_CLEANER_PROTO = CFUNCTYPE(None, POINTER(z_array_resource_t), POINTER(c_int64))
ZENOH_QUERY_HANDLER_PROTO = CFUNCTYPE(None, c_char_p, c_char_p, POINTER(z_array_resource_t), POINTER(c_int64))

@ZENOH_SUBSCRIBER_CALLBACK_PROTO
def z_subscriber_trampoline_callback(rid, data, length, info, arg):
  global subscriberCallbackMap
  key = arg.contents.value  
  _, callback = subscriberCallbackMap[key]  
  if rid.contents.kind == Z_STR_RES_ID:          
    callback(rid.contents.id.rname.decode(), data[:length], info.contents)
  else:
    print('WARNING: Received data for unknown  resource name, rid = {}'.format(rid.id.rid))

@ZENOH_REPLY_CALLBACK_PROTO
def z_reply_trampoline_callback(reply_value, arg):
  global replyCallbackMap
  key = arg.contents.value  
  _, callback = replyCallbackMap[key] 
  qr = QueryReply(reply_value.contents)   
  callback(qr)

@ZENOH_QUERY_HANDLER_PROTO
def z_query_handler_trampoline(rname, predicate, p_replies, arg):
  global queryHandlerMap
  key = arg.contents.value
  _, handler = queryHandlerMap[key]
  kvs =  handler(rname.decode(), predicate.decode())
  l = len(kvs)
  p_replies.contents.length = l
  rs = (POINTER(z_resource_t) * l)()  
  p_replies.contents.elem = cast(rs, POINTER(POINTER(z_resource_t)))
  i = 0
  for k,v in kvs:        
    d, info = v
    p_replies.contents.elem[i].contents = z_resource_t()
    p_replies.contents.elem[i].contents.rname = k.encode()
    p_replies.contents.elem[i].contents.data = d
    p_replies.contents.elem[i].contents.length = len(d)
    p_replies.contents.elem[i].contents.encoding = info.encoding
    p_replies.contents.elem[i].contents.kind = info.kind
    i += 1    
  
  replyMap[key] = p_replies.contents

@ZENOH_REPLY_CLEANER_PROTO
def z_no_op_reply_cleaner(replies, args):  
  key = args.contents.value
  del replyMap[key]
  return
