import platform
import os
from ctypes import *


Z_INT_RES_ID = 0
Z_STR_RES_ID = 1


Z_PUT       = 0x00
Z_UPDATE    = 0x01
Z_REMOVE    = 0x02


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


ZENOH_ON_DISCONNECT_CALLBACK_PROTO = CFUNCTYPE(None, c_void_p)
ZENOH_SUBSCRIBER_CALLBACK_PROTO = CFUNCTYPE(None, z_resource_id_t, CHAR_PTR, c_uint, z_data_info_t)
ZENOH_REPLY_CALLBACK = CFUNCTYPE(None, z_reply_value_t)

class SubscriberCallback(object):
    def __init__(self, callback):
        self.callback = callback

    @ZENOH_SUBSCRIBER_CALLBACK_PROTO
    def trampoline_callback(self, rid, data, length, info):
        self.callback(rid, data, length, info)
