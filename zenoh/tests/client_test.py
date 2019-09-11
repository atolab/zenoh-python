import unittest
import time
from mvar import MVar
import zenoh


z1_sub1_mvar = MVar()
z2_sub1_mvar = MVar()
z1_sto1_last_res = None
z1_sto1_mvar = MVar()
z2_sto1_last_res = None
z2_sto1_mvar = MVar()
storage_replies = []
eval_replies = []
replies_mvar = MVar()


def z1_sub1_listener(rname, data, info):
    z1_sub1_mvar.put((rname, data))


def z2_sub1_listener(rname, data, info):
    z2_sub1_mvar.put((rname, data))


def z1_sto1_listener(rname, data, info):
    global z1_sto1_last_res
    z1_sto1_last_res = (rname, (data, info))
    z1_sto1_mvar.put((rname, data))


def z2_sto1_listener(rname, data, info):
    global z2_sto1_last_res
    z2_sto1_last_res = (rname, (data, info))
    z2_sto1_mvar.put((rname, data))


def z1_sto1_handler(path_selector, content_selector, send_replies):
    send_replies([z1_sto1_last_res])


def z2_sto1_handler(path_selector, content_selector, send_replies):
    send_replies([z2_sto1_last_res])


def z1_eval1_handler(path_selector, content_selector, send_replies):
    send_replies([("/test/python/client/z1_eval1",
                   ("z1_eval1_data".encode(), zenoh.DataInfo()))])


def z2_eval1_handler(path_selector, content_selector, send_replies):
    send_replies([("/test/python/client/z2_eval1",
                   ("z2_eval1_data".encode(), zenoh.DataInfo()))])


def reply_handler(reply):
    if reply.kind == zenoh.Z_STORAGE_DATA:
        storage_replies.append((reply.rname, reply.data))
    if reply.kind == zenoh.Z_EVAL_DATA:
        eval_replies.append((reply.rname, reply.data))
    elif reply.kind == zenoh.Z_REPLY_FINAL:
        replies_mvar.put((storage_replies, eval_replies))


class ClientTest(unittest.TestCase):
    def client_test(self):
        global storage_replies
        global eval_replies
        locator = "tcp/127.0.0.1:7447"

        z1 = zenoh.Zenoh(locator)
        z1_peer = z1.info()[zenoh.Z_INFO_PEER_KEY].decode().rstrip('\0')
        self.assertEqual(locator, z1_peer)
        z1_sub1 = z1.declare_subscriber("/test/python/client/**",
                                        zenoh.SubscriberMode.push(),
                                        z1_sub1_listener)
        z1_sto1 = z1.declare_storage("/test/python/client/**",
                                     z1_sto1_listener,
                                     z1_sto1_handler)
        z1_eval1 = z1.declare_eval("/test/python/client/z1_eval1",
                                     z1_eval1_handler)
        z1_pub1 = z1.declare_publisher("/test/python/client/z1_pub1")

        z2 = zenoh.Zenoh(locator)
        z2_peer = z2.info()[zenoh.Z_INFO_PEER_KEY].decode().rstrip('\0')
        self.assertEqual(locator, z2_peer)
        z2_sub1 = z2.declare_subscriber("/test/python/client/**",
                                        zenoh.SubscriberMode.push(),
                                        z2_sub1_listener)
        z2_sto1 = z2.declare_storage("/test/python/client/**",
                                     z2_sto1_listener,
                                     z2_sto1_handler)
        z2_eval1 = z2.declare_eval("/test/python/client/z2_eval1",
                                     z2_eval1_handler)
        z2_pub1 = z2.declare_publisher("/test/python/client/z2_pub1")

        time.sleep(1)

        self.assertTrue(z1.running)
        self.assertTrue(z2.running)

        sent_res = ("/test/python/client/z1_wr1", "z1_wr1_spl1".encode())
        z1.write_data(sent_res[0], sent_res[1])
        rcvd_res = z1_sub1_mvar.get()
        self.assertEqual(sent_res, rcvd_res)
        rcvd_res = z2_sub1_mvar.get()
        self.assertEqual(sent_res, rcvd_res)
        rcvd_res = z1_sto1_mvar.get()
        self.assertEqual(sent_res, rcvd_res)
        rcvd_res = z2_sto1_mvar.get()
        self.assertEqual(sent_res, rcvd_res)

        z1.query("/test/python/client/**", "", reply_handler)
        replies_mvar.get()
        self.assertEqual(2, len(storage_replies))
        self.assertEqual(sent_res, storage_replies[0])
        self.assertEqual(sent_res, storage_replies[1])
        storage_replies = []
        self.assertEqual(2, len(eval_replies))
        eval_replies = []

        z2.query("/test/python/client/**", "", reply_handler)
        replies_mvar.get()
        self.assertEqual(2, len(storage_replies))
        self.assertEqual(sent_res, storage_replies[0])
        self.assertEqual(sent_res, storage_replies[1])
        storage_replies = []
        self.assertEqual(2, len(eval_replies))
        eval_replies = []

        sent_res = ("/test/python/client/**", "z2_wr1_spl1".encode())
        z2.write_data(sent_res[0], sent_res[1])
        rcvd_res = z1_sub1_mvar.get()
        self.assertEqual(sent_res, rcvd_res)
        rcvd_res = z2_sub1_mvar.get()
        self.assertEqual(sent_res, rcvd_res)
        rcvd_res = z1_sto1_mvar.get()
        self.assertEqual(sent_res, rcvd_res)
        rcvd_res = z2_sto1_mvar.get()
        self.assertEqual(sent_res, rcvd_res)

        z1.query("/test/python/client/**", "", reply_handler)
        replies_mvar.get()
        self.assertEqual(2, len(storage_replies))
        self.assertEqual(sent_res, storage_replies[0])
        self.assertEqual(sent_res, storage_replies[1])
        storage_replies = []
        self.assertEqual(2, len(eval_replies))
        eval_replies = []

        z2.query("/test/python/client/**", "", reply_handler)
        replies_mvar.get()
        self.assertEqual(2, len(storage_replies))
        self.assertEqual(sent_res, storage_replies[0])
        self.assertEqual(sent_res, storage_replies[1])
        storage_replies = []
        self.assertEqual(2, len(eval_replies))
        eval_replies = []

        sent_res = ("/test/python/client/z1_pub1", "z1_pub1_spl1".encode())
        z1.stream_data(z1_pub1, sent_res[1])
        rcvd_res = z1_sub1_mvar.get()
        self.assertEqual(sent_res, rcvd_res)
        rcvd_res = z2_sub1_mvar.get()
        self.assertEqual(sent_res, rcvd_res)
        rcvd_res = z1_sto1_mvar.get()
        self.assertEqual(sent_res, rcvd_res)
        rcvd_res = z2_sto1_mvar.get()
        self.assertEqual(sent_res, rcvd_res)

        z1.query("/test/python/client/**", "", reply_handler)
        replies_mvar.get()
        self.assertEqual(2, len(storage_replies))
        self.assertEqual(sent_res, storage_replies[0])
        self.assertEqual(sent_res, storage_replies[1])
        storage_replies = []
        self.assertEqual(2, len(eval_replies))
        eval_replies = []

        z2.query("/test/python/client/**", "", reply_handler)
        replies_mvar.get()
        self.assertEqual(2, len(storage_replies))
        self.assertEqual(sent_res, storage_replies[0])
        self.assertEqual(sent_res, storage_replies[1])
        storage_replies = []
        self.assertEqual(2, len(eval_replies))
        eval_replies = []

        sent_res = ("/test/python/client/z2_pub1", "z2_pub1_spl1".encode())
        z2.stream_data(z2_pub1, sent_res[1])
        rcvd_res = z1_sub1_mvar.get()
        self.assertEqual(sent_res, rcvd_res)
        rcvd_res = z2_sub1_mvar.get()
        self.assertEqual(sent_res, rcvd_res)
        rcvd_res = z1_sto1_mvar.get()
        self.assertEqual(sent_res, rcvd_res)
        rcvd_res = z2_sto1_mvar.get()
        self.assertEqual(sent_res, rcvd_res)

        z1.query("/test/python/client/**", "", reply_handler)
        replies_mvar.get()
        self.assertEqual(2, len(storage_replies))
        self.assertEqual(sent_res, storage_replies[0])
        self.assertEqual(sent_res, storage_replies[1])
        storage_replies = []
        self.assertEqual(2, len(eval_replies))
        eval_replies = []

        z2.query("/test/python/client/**", "", reply_handler)
        replies_mvar.get()
        self.assertEqual(2, len(storage_replies))
        self.assertEqual(sent_res, storage_replies[0])
        self.assertEqual(sent_res, storage_replies[1])
        storage_replies = []
        self.assertEqual(2, len(eval_replies))
        eval_replies = []

        z1.undeclare_subscriber(z1_sub1)
        z2.undeclare_subscriber(z2_sub1)
        z1.undeclare_storage(z1_sto1)
        z2.undeclare_storage(z2_sto1)
        z1.undeclare_eval(z1_eval1)
        z2.undeclare_eval(z2_eval1)
        z1.undeclare_publisher(z1_pub1)
        z2.undeclare_publisher(z2_pub1)

        z1.close()
        z2.close()

        time.sleep(1)  # let time for close msg to comme back from router

        self.assertFalse(z1.running)
        self.assertFalse(z2.running)
