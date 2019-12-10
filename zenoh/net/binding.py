import platform
import os
import ctypes
import datetime
import binascii
import traceback
from ctypes import *
from functools import partial

Z_INT_RES_ID = 0
Z_STR_RES_ID = 1


Z_PUT = 0x00
Z_UPDATE = 0x01
Z_REMOVE = 0x02

Z_STORAGE_DATA = 0x00
Z_STORAGE_FINAL = 0x01
Z_EVAL_DATA = 0x02
Z_EVAL_FINAL = 0x03
Z_REPLY_FINAL = 0x04

Z_OK_TAG = 0
Z_ERROR_TAG = 1

Z_SRC_ID = 0x01
Z_SRC_SN = 0x02
Z_BRK_ID = 0x04
Z_BRK_SN = 0x08
Z_T_STAMP = 0x10
Z_KIND = 0x20
Z_ENCODING = 0x40

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


class z_eval_p_result_union_t(Union):
    _fields_ = [('eval', c_void_p), ('error', c_int)]


class z_eval_p_result_t(Structure):
    _fields_ = [('tag', c_int), ('value', z_eval_p_result_union_t)]


class z_vec_t(Structure):
    _fields_ = [('capacity', c_int), ('length', c_int), ('elem', c_void_p)]


# Resource Id
class z_res_id_t(Union):
    _fields_ = [('rid', c_int), ('rname', c_char_p)]


class z_resource_id_t(Structure):
    _fields_ = [('kind', c_int), ('id', z_res_id_t)]


# TimeStamp
class z_timestamp_t(Structure):
    _fields_ = [('clock_id', c_uint8 * 16),
                ('time', c_size_t)]

    def __hash__(self):
        return hash((self.time, self.clock_id[0], self.clock_id[1],
                     self.clock_id[2], self.clock_id[3], self.clock_id[4],
                     self.clock_id[5], self.clock_id[6], self.clock_id[7],
                     self.clock_id[8], self.clock_id[9], self.clock_id[10],
                     self.clock_id[11], self.clock_id[12], self.clock_id[13],
                     self.clock_id[14], self.clock_id[15]))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.time != other.time:
                return False
            for i in range(0, 15):
                if self.clock_id[i] != other.clock_id[i]:
                    return False
            return True

    def __lt__(self, other):
        if self.time < other.time:
            return True
        if self.time > other.time:
            return False
        for i in range(0, 15):
            if self.clock_id[i] < other.clock_id[i]:
                return True
            if self.clock_id[i] > other.clock_id[i]:
                return False
        return False

    def __str__(self):
        sec = self.time >> 32
        time = datetime.datetime.utcfromtimestamp(float(sec))
        frac = self.time & 0xffffffff
        ns = int((frac * 1000000000) / 0x100000000)
        id = binascii.hexlify(self.clock_id).decode("ascii")
        return "{}.{:09d}Z/{}".format(time.isoformat(), ns, id)

    def floattime(self):
        """
        Return the Timestamp's creation time as a float
        (i.e. number of seconds since Epoch:  January 1, 1970, 00:00:00 (UTC))
        Warning: the time might be rounded, depending the float precision on
        your host.
        """
        sec = self.time >> 32
        frac = self.time & 0xffffffff
        ns = float(frac) / 0x100000000
        return sec + ns

    def datetime(self, tzinfo):
        """
        Return the Timestamp's creation time as a datetime.datetime
        Warning: the time is rounded to milliseconds as datetime precision
        is millisecond.
        """
        return datetime.datetime.fromtimestamp(self.floattime(), tzinfo)


# Data Info
class z_data_info_t(Structure):
    _fields_ = [('flags', c_uint),
                ('tstamp', z_timestamp_t),
                ('encoding', c_uint8),
                ('kind', c_ushort)]


class DataInfo():
    """
    An object containing meta informations about some associated data.

    kind
        The kind of the data.
    encoding
        The encoding of the data.
    tstamp
        The unique timestamp at which the data was produced.

    """

    def __init__(self, kind=None, encoding=None, tstamp=None):
        self.kind = kind
        self.tstamp = tstamp
        self.encoding = encoding

    @staticmethod
    def from_z_data_info(z_info):
        return DataInfo(
            kind=z_info.kind if z_info.flags & Z_KIND else None,
            encoding=z_info.encoding if z_info.flags & Z_ENCODING else None,
            tstamp=z_info.tstamp if z_info.flags & Z_T_STAMP else None
        )


# Query destination
class z_query_dest_t(Structure):
    _fields_ = [('kind', c_uint8), ('nb', c_uint8)]


# Temporal properties
class z_temporal_property_t(Structure):
    _fields_ = [('origin', c_int), ('period', c_int), ('duration', c_int)]


class z_sub_mode_t(Structure):
    _fields_ = [('kind', c_uint8), ('tprop', z_temporal_property_t)]


# properties
class z_array_uint8_t(Structure):
    _fields_ = [
        ('length', c_uint),
        ('elem', POINTER(c_char))]


class z_property_t(Structure):
    _fields_ = [('id', c_size_t), ('value', z_array_uint8_t)]


def dict_to_propsvec(props):
    length = len(props)
    elems = [POINTER(z_property_t)(z_property_t(
                key, z_array_uint8_t(
                        len(val),
                        ctypes.create_string_buffer(val, len(val)))))
             for key, val in props.items()]
    return POINTER(z_vec_t)(z_vec_t(
        length, length,
        cast(((POINTER(z_property_t) * length)(*elems)), c_void_p)))


def propsvec_to_dict(vec):
    vectype = POINTER((POINTER(z_property_t) * vec.length))
    props = [prop[0] for prop in cast(vec.elem, vectype)[0]]
    return {prop.id: prop.value.elem[:prop.value.length] for prop in props}


CHAR_PTR = POINTER(c_char)


# zenoh-c callbacks
class z_reply_value_t(Structure):
    _fields_ = [
        ('kind', c_uint8),
        ('srcid', CHAR_PTR),
        ('srcid_length', c_size_t),
        ('rsn', c_uint32),
        ('rname', c_char_p),
        ('data', CHAR_PTR),
        ('data_length', c_size_t),
        ('info', z_data_info_t)]


class QueryReply(object):
    """
    An object containing one of the replies to a :func:`Session.query`.

    kind
        One of the following:

        | ``Z_STORAGE_DATA`` the reply contains some data from a storage.
        | ``Z_STORAGE_FINAL`` the reply indicates that no more data is
            expected from the specified storage.
        | ``Z_EVAL_DATA`` the reply contains some data from an eval.
        | ``Z_EVAL_FINAL`` the reply indicates that no more data is expected
            from the specified eval.
        | ``Z_REPLY_FINAL`` the reply indicates that no more replies are
            expected for the query.

    source_id
        The unique identifier of the storage or eval that sent the reply
        when `kind` equals ``Z_STORAGE_DATA``, ``Z_STORAGE_FINAL``,
        ``Z_EVAL_DATA`` or ``Z_EVAL_FINAL``.
    seq_num
        The sequence number of the reply from the identified storage or
        eval when `kind` equals ``Z_STORAGE_DATA``, ``Z_STORAGE_FINAL``,
        ``Z_EVAL_DATA`` or ``Z_EVAL_FINAL``.
    rname
        The resource name of the received data when `kind` equals
        ``Z_STORAGE_DATA`` or ``Z_EVAL_DATA``.
    data
        The received data when `kind` equals ``Z_STORAGE_DATA`` or
        ``Z_EVAL_DATA``.
    info
        A :class:`DataInfo` object holding meta information about the received
        data when `kind` equals ``Z_STORAGE_DATA`` or ``Z_EVAL_DATA``.

    """

    def __init__(self, zrv):
        self.kind = zrv.kind
        self.source_id = None
        self.seq_num = None
        self.rname = None
        self.data = None
        self.info = None

        if(self.kind == Z_STORAGE_DATA
           or self.kind == Z_EVAL_DATA):
            self.source_id = zrv.srcid[:zrv.srcid_length]
            self.seq_num = zrv.rsn
            self.rname = zrv.rname.decode()
            self.data = zrv.data[:zrv.data_length]
            self.info = z_data_info_t()
            self.info.flags = zrv.info.flags
            self.info.tstamp.clock_id = zrv.info.tstamp.clock_id
            self.info.tstamp.time = zrv.info.tstamp.time
            self.info.encoding = zrv.info.encoding
            self.info.kind = zrv.info.kind

        elif(self.kind == Z_STORAGE_FINAL
             or self.kind == Z_EVAL_FINAL):
            self.source_id = zrv.srcid[:zrv.srcid_length]


class z_resource_t(Structure):
    _fields_ = [
        ('rname', c_char_p),
        ('data', c_char_p),
        ('length', c_size_t),
        ('encoding', c_ushort),
        ('kind', c_ushort)
    ]


class z_array_p_resource_t(Structure):
    _fields_ = [
        ('length', c_uint),
        ('elem', POINTER(POINTER(z_resource_t)))
    ]


ZENOH_ON_DISCONNECT_CALLBACK_PROTO = CFUNCTYPE(None, c_void_p)
ZENOH_SUBSCRIBER_CALLBACK_PROTO = CFUNCTYPE(None,
                                            POINTER(z_resource_id_t),
                                            CHAR_PTR, c_uint,
                                            POINTER(z_data_info_t),
                                            POINTER(c_int64))
ZENOH_REPLY_CALLBACK_PROTO = CFUNCTYPE(None,
                                       POINTER(z_reply_value_t),
                                       POINTER(c_int64))
ZENOH_SEND_REPLIES_PROTO = CFUNCTYPE(None,
                                     POINTER(c_int64),
                                     z_array_p_resource_t)
ZENOH_QUERY_HANDLER_PROTO = CFUNCTYPE(None,
                                      c_char_p,
                                      c_char_p,
                                      ZENOH_SEND_REPLIES_PROTO,
                                      POINTER(c_int64),
                                      POINTER(c_int64))


@ZENOH_SUBSCRIBER_CALLBACK_PROTO
def z_subscriber_trampoline_callback(rid, data, length, info, arg):
    global subscriberCallbackMap
    key = arg.contents.value
    _, callback = subscriberCallbackMap[key]
    if rid.contents.kind == Z_STR_RES_ID:
        py_info = DataInfo.from_z_data_info(info.contents)
        callback(rid.contents.id.rname.decode(), data[:length], py_info)
    else:
        print('WARNING: Received data for unknown  resource name, rid = {}'
              .format(rid.id.rid))


@ZENOH_REPLY_CALLBACK_PROTO
def z_reply_trampoline_callback(reply_value, arg):
    global replyCallbackMap
    key = arg.contents.value
    _, callback = replyCallbackMap[key]
    qr = QueryReply(reply_value.contents)
    callback(qr)


def send_replies_fun(send_replies, query_handle, replies):
    replies_array = z_array_p_resource_t()
    replies_array.length = len(replies)
    rs = (POINTER(z_resource_t) * len(replies))()
    replies_array.elem = cast(rs, POINTER(POINTER(z_resource_t)))
    i = 0
    for k, v in replies:
        d, info = v
        replies_array.elem[i].contents = z_resource_t()
        replies_array.elem[i].contents.rname = k.encode()
        replies_array.elem[i].contents.data = d
        replies_array.elem[i].contents.length = len(d)

        encoding_not_none = info is not None and info.encoding is not None
        encoding = info.encoding if encoding_not_none else 0
        replies_array.elem[i].contents.encoding = encoding

        kind_not_none = info is not None and info.kind is not None
        kind = info.kind if kind_not_none else 0
        replies_array.elem[i].contents.kind = kind

        tstamp_not_none = info is not None and info.tstamp is not None
        tstamp = info.tstamp if tstamp_not_none else 0
        replies_array.elem[i].contents.tstamp = tstamp

        i += 1
    send_replies(query_handle, replies_array)


@ZENOH_QUERY_HANDLER_PROTO
def z_query_handler_trampoline(rname,
                               predicate,
                               send_replies,
                               query_handle,
                               arg):
    global queryHandlerMap
    key = arg.contents.value
    _, handler = queryHandlerMap[key]
    try:
        handler(rname.decode(), predicate.decode(),
                partial(send_replies_fun, send_replies, query_handle))
    except Exception:
        print('WARNING: error in query handle for {} :\n{}'
              .format(rname.decode(), traceback.format_exc()))
        send_replies_fun(send_replies, query_handle, [])
