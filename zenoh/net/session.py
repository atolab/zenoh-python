from .binding import *
import socket
import time

Z_USER_KEY = 0x50
Z_PASSWD_KEY = 0x51

Z_INFO_PID_KEY = 0
Z_INFO_PEER_KEY = 1
Z_INFO_PEER_PID_KEY = 2


class SubscriberMode(object):
    """
    An object representing a subscription mode
    (see :func:`Session.declare_subscriber`).

    kind
        One of the following:

        | ``SubscriberMode.Z_PUSH_MODE``
        | ``SubscriberMode.Z_PULL_MODE``
        | ``SubscriberMode.Z_PERIODIC_PUSH_MODE``
        | ``SubscriberMode.Z_PERIODIC_PULL_MODE``

    tprop
        A temporal property representing the period. `Unsupported`

    """

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
        """
        Return a SubscriberMode instance with `kind` =
        ``SubscriberMode.Z_PUSH_MODE``

        :returns: the equivalent of
            ``SubscriberMode(SubscriberMode.Z_PUSH_MODE, None)``
        """
        return SubscriberMode(SubscriberMode.Z_PUSH_MODE, None)

    @staticmethod
    def pull():
        """
        Return a SubscriberMode instance with `kind` =
        ``SubscriberMode.Z_PULL_MODE``

        :returns: the equivalent of
            ``SubscriberMode(SubscriberMode.Z_PULL_MODE, None)``
        """
        return SubscriberMode(SubscriberMode.Z_PULL_MODE, None)


class QueryDest(object):
    """
    An object defining which storages or evals should be destination of a
    query (see :func:`Session.query`).

    kind
        One of the following:

        | ``SubscriberMode.Z_BEST_MATCH``
        | ``SubscriberMode.Z_COMPLETE``
        | ``SubscriberMode.Z_ALL``
        | ``SubscriberMode.Z_NONE``

    nb
        The number of storages or evals that should be destination of
        the query when `kind` equals ``SubscriberMode.Z_COMPLETE``.

    """
    Z_BEST_MATCH = 0
    Z_COMPLETE = 1
    Z_ALL = 2
    Z_NONE = 3

    def __init__(self, kind, nb=1):
        self.z_qd = z_query_dest_t()
        self.z_qd.kind = kind
        self.z_qd.nb = nb


def z_to_canonical_locator(locator):
    if locator is None:
        return None
    locator = locator.strip()
    a, b, c = locator.partition('/')
    if a == 'tcp' and b == '/':
        h, s, p = c.partition(':')
        if s == ':' and p != '':
            return ('tcp/' + socket.gethostbyname(h) + ':' + p).encode()
        else:
            raise Exception('Invalid locator format {}, it should be '
                            'tcp/<ip-addr|host-name>:port'.format(locator))
    elif b == '':
        h, s, p = locator.partition(':')
        if s == ':':
            return ('tcp/' + socket.gethostbyname(h) + ':' + p).encode()
        else:
            return ('tcp/' + socket.gethostbyname(h) + ':7447').encode()


def rname_intersect(a, b):
    if Session.zenoh_native_lib.intersect(a.encode(), b.encode()) == 1:
        return True
    else:
        return False


class Session(object):
    """
    An object that represents a zenoh session.
    """

    zenoh_native_lib = None

    def __init__(self, locator, properties={}):
        if Session.zenoh_native_lib is None:
            Session.zenoh_native_lib = CDLL(zenoh_lib_path)

        self.zlib = Session.zenoh_native_lib

        self.zlib.z_open.restype = z_zenoh_p_result_t
        self.zlib.z_open.argtypes = [c_char_p, c_void_p, POINTER(z_vec_t)]

        self.zlib.z_info.restype = z_vec_t
        self.zlib.z_info.argtypes = [c_void_p]

        self.zlib.z_running.restype = c_int
        self.zlib.z_running.argtypes = [c_void_p]

        self.zlib.z_declare_subscriber.restype = z_sub_p_result_t
        self.zlib.z_declare_subscriber.argtypes = [
            c_void_p, c_char_p, POINTER(z_sub_mode_t),
            ZENOH_SUBSCRIBER_CALLBACK_PROTO, POINTER(c_int64)]

        self.zlib.z_declare_storage.restype = z_sto_p_result_t
        self.zlib.z_declare_storage.argtypes = [
            c_void_p, c_char_p, ZENOH_SUBSCRIBER_CALLBACK_PROTO,
            ZENOH_QUERY_HANDLER_PROTO, POINTER(c_int64)]

        self.zlib.z_declare_eval.restype = z_eval_p_result_t
        self.zlib.z_declare_eval.argtypes = [
            c_void_p, c_char_p, ZENOH_QUERY_HANDLER_PROTO,
            POINTER(c_int64)]

        self.zlib.z_declare_publisher.restype = z_pub_p_result_t
        self.zlib.z_declare_publisher.argtypes = [c_void_p, c_char_p]

        self.zlib.z_start_recv_loop.restype = c_int
        self.zlib.z_start_recv_loop.argtypes = [c_void_p]

        self.zlib.z_stop_recv_loop.restype = c_int
        self.zlib.z_stop_recv_loop.argtypes = [c_void_p]

        self.zlib.z_stream_compact_data.restype = c_int
        self.zlib.z_stream_compact_data.argtypes = [
            c_void_p, POINTER(c_char), c_int]

        self.zlib.z_stream_data_wo.restype = c_int
        self.zlib.z_stream_data_wo.argtypes = [
            c_void_p, c_char_p, c_int, c_uint8, c_uint8]

        self.zlib.z_write_data_wo.restype = c_int
        self.zlib.z_write_data_wo.argtypes = [
            c_void_p, c_char_p, c_char_p, c_int, c_uint8, c_uint8]

        self.zlib.z_pull.restype = c_int
        self.zlib.z_pull.argtypes = [c_void_p]

        self.zlib.z_query_wo.restype = c_int
        self.zlib.z_query_wo.argtypes = [
            c_void_p, c_char_p, c_char_p,
            ZENOH_REPLY_CALLBACK_PROTO, POINTER(c_int64),
            z_query_dest_t, z_query_dest_t]

        self.zlib.z_undeclare_subscriber.restype = c_int
        self.zlib.z_undeclare_subscriber.argtypes = [c_void_p]

        self.zlib.z_undeclare_storage.restype = c_int
        self.zlib.z_undeclare_storage.argtypes = [c_void_p]

        self.zlib.z_undeclare_eval.restype = c_int
        self.zlib.z_undeclare_eval.argtypes = [c_void_p]

        self.zlib.z_undeclare_publisher.restype = c_int
        self.zlib.z_undeclare_publisher.argtypes = [c_void_p]

        self.zlib.z_close.restype = c_int
        self.zlib.z_close.argtypes = [c_void_p]

        self.zlib.intersect.restype = c_int
        self.zlib.intersect.argtypes = [c_char_p, c_char_p]

        loc = z_to_canonical_locator(locator)

        r = self.zlib.z_open(loc, 0, dict_to_propsvec(properties))
        if r.tag == Z_OK_TAG:
            self.zenoh = r.value.zenoh
            self.connected = True
        else:
            raise Exception('Unable to open zenoh session (error code: {}).'
                            .format(r.value.error))

        self.zlib.z_start_recv_loop(self.zenoh)
        while not self.running:
            time.sleep(0.01)

    @staticmethod
    def open(locator=None, properties={}):
        """
        Open a zenoh session.

        :param locator: a string representing the network endpoint to which
            establish the session. A typical locator looks like this :
            ``tcp/127.0.0.1:7447``. If ``None``, :func:`open` will scout and
            try to establish the session automatically.
        :param properties: a {int: bytes} dictionary of properties that will
            be used to establish and configure the zenoh session.
            **properties** will typically contain the username and
            password informations needed to establish the zenoh session
            with a secured infrastructure. It can be set to ``NULL``.
        :returns: a handle to the zenoh session.

        """
        return Session(locator, properties)

    def info(self):
        """
        Return a {int: bytes} dictionary of properties containing various
        informations about the established zenoh session.

        :returns: a {int: bytes} dictionary of properties.

        """
        return propsvec_to_dict(self.zlib.z_info(self.zenoh))

    @property
    def running(self):
        return (self.zlib.z_running(self.zenoh) != 0)

    def declare_publisher(self, res_name):
        """
        Declare a publication for resource **res_name**.

        :param res_name: is the resource name to publish.
        :returns: a zenoh publisher.

        """
        r = self.zlib.z_declare_publisher(self.zenoh, res_name.encode())
        if r.tag == 0:
            return r.value.pub
        else:
            raise Exception('Unable to create publisher')

    def declare_subscriber(self, selector, sub_mode, callback):
        """
        Declare a subscription for all published data matching the provided
        resource **selector**.

        :param selector: the selection of resource to subscribe to.
        :param sub_mode: the subscription mode.
        :param callback: the callback function that will be called each time a
            data matching the subscribed resource is received.
        :returns: a zenoh subscriber.

        """
        global subscriberCallbackMap
        h = hash(callback)
        k = POINTER(c_int64)(c_int64(h))
        r = self.zlib.z_declare_subscriber(self.zenoh,
                                           selector.encode(),
                                           byref(sub_mode.z_sm),
                                           z_subscriber_trampoline_callback,
                                           k)
        subscriberCallbackMap[h] = (k, callback)
        if r.tag == 0:
            return r.value.sub
        else:
            del subscriberCallbackMap[h]
            raise Exception('Unable to create subscriber')

    def declare_storage(self, selector, subscriber_callback, query_handler):
        """
        Declare a storage for all data matching the provided resource
        **selector**.

        :param selector: the selection of resources to store.
        :param subscriber_callback: the callback function that will be called
            each time a data matching the stored selection is received.
        :param query_handler: the callback function that will be called each
            time a query for data matching the stored selection is received.
            The **query_handler** function MUST call the provided
            **send_replies** function with the resulting data.
            **send_replies** can be called with an empty array.
        :returns: a zenoh storage.

        """
        global replyCallbackMap
        h = hash(query_handler)
        k = POINTER(c_int64)(c_int64(h))
        subscriberCallbackMap[h] = (k, subscriber_callback)
        queryHandlerMap[h] = (k, query_handler)
        r = self.zlib.z_declare_storage(
                self.zenoh,
                selector.encode(),
                z_subscriber_trampoline_callback,
                z_query_handler_trampoline,
                k)
        if r.tag == 0:
            return r.value.sto
        else:
            del subscriberCallbackMap[h]
            del replyCallbackMap[h]
            raise Exception('Unable to create storage')

    def declare_eval(self, selector, query_handler):
        """
        Declare an eval able to provide data matching the provided resource
        **selector**.

        :param selector: the selection of resources to evaluate.
        :param query_handler: is the callback function that will be called
            each time a query for data matching the evaluated **selector**
            is received. The **query_handler** function MUST call the provided
            **send_replies** function with the resulting data.
            **send_replies** can be called with an empty array.
        :returns: a zenoh eval.

        """
        global replyCallbackMap
        h = hash(query_handler)
        k = POINTER(c_int64)(c_int64(h))
        queryHandlerMap[h] = (k, query_handler)
        r = self.zlib.z_declare_eval(
                self.zenoh,
                selector.encode(),
                z_query_handler_trampoline,
                k)
        if r.tag == 0:
            return r.value.eval
        else:
            del replyCallbackMap[h]
            raise Exception('Unable to create eval')

    def stream_compact_data(self, pub, data):
        """
        Send data in a *compact_data* message for the resource published by
        publisher **pub**.

        :param pub: the publisher to use to send data.
        :param payload: a pointer to the data to be sent.
        :param len: the size of the data to be sent.
        :returns: 0 if the publication is successful.

        """
        self.zlib.z_stream_compact_data(pub, data, len(data))

    def stream_data(self, pub, data, encoding=0, kind=Z_PUT):
        """
        Send data in a *stream_data* message for the resource published by
        publisher **pub**.

        :param pub: the publisher to use to send data.
        :param data: the data to be sent as bytes.
        :param encoding: a metadata information associated with the published
            data that represents the encoding of the published data.
        :param kind: a metadata information associated with the published
            data that represents the kind of publication.
        :returns: 0 if the publication is successful.

        """
        self.zlib.z_stream_data_wo(pub, data, len(data), encoding, kind)

    def write_data(self, resource, data, encoding=0, kind=Z_PUT):
        """
        Send data in a *write_data* message for the resource **resource**.

        :param resource: the resource name of the data to be sent.
        :param data: the data to be sent as bytes.
        :param encoding: a metadata information associated with the published
            data that represents the encoding of the published data.
        :param kind: a metadata information associated with the published
            data that represents the kind of publication.
        :returns: 0 if the publication is successful.
        """
        self.zlib.z_write_data_wo(self.zenoh,
                                  resource.encode(),
                                  data,
                                  len(data),
                                  encoding,
                                  kind)

    def pull(self, sub):
        """
        Pull data for the `Z_PULL_MODE` or `Z_PERIODIC_PULL_MODE` subscribtion
        **sub** from the nearest infrastruture component. The pulled data will
        be provided by calling the **data_handler** function provided to the
        **declare_subscriber** function.

        :param sub: the subscribtion to pull from.
        :returns: 0 if pull is successful.
        """
        self.zlib.z_pull(sub)

    def query(self, selector, predicate, callback,
              dest_storages=QueryDest(QueryDest.Z_BEST_MATCH),
              dest_evals=QueryDest(QueryDest.Z_BEST_MATCH)):
        """
        Query data matching selection **selector**.

        :param selector: the selection of resource to query.
        :param predicate: a string that will be  propagated to the storages
            and evals that should provide the queried data. It may allow them
            to filter, transform and/or compute the queried data.
        :param reply_handler: the callback function that will be called on
            reception of the replies of the query.
        :param dest_storages: indicates which matching storages should be
            destination of the query (see :class:`QueryDest`).
        :param dest_evals: indicates which matching evals should be
            destination of the query (see :class:`QueryDest`).
        :returns: 0 if the query is sent successfully.
        """
        global replyCallbackMap
        h = hash(callback)
        k = POINTER(c_int64)(c_int64(h))
        replyCallbackMap[h] = (k, callback)
        r = self.zlib.z_query_wo(self.zenoh,
                                 selector.encode(),
                                 predicate.encode(),
                                 z_reply_trampoline_callback,
                                 k,
                                 dest_storages.z_qd,
                                 dest_evals.z_qd)
        if r != 0:
            del replyCallbackMap[h]
            raise Exception('Unable to create query')

    def undeclare_publisher(self, pub):
        """
        Undeclare the publication **pub**.

        :param pub: the publication to undeclare.
        :returns: 0 when successful.

        """
        self.zlib.z_undeclare_publisher(pub)

    def undeclare_subscriber(self, sub):
        """
        Undeclare the subscrbtion **sub**.

        :param sub: the subscription to undeclare.
        :returns: 0 when successful.

        """
        self.zlib.z_undeclare_subscriber(sub)

    def undeclare_storage(self, sto):
        """
        Undeclare the storage **sto**.

        :param sto: the storage to undeclare.
        :returns: 0 when successful.

        """
        self.zlib.z_undeclare_storage(sto)

    def undeclare_eval(self, eval):
        """
        Undeclare the eval **eval**.

        :param eval: the eval to undeclare.
        :returns: 0 when successful.

        """
        self.zlib.z_undeclare_eval(eval)

    def close(self):
        """
            Close the zenoh session.
        """
        self.zlib.z_close(self.zenoh)
        self.zlib.z_stop_recv_loop(self.zenoh)
