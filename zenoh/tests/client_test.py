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
replies = []
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


def reply_handler(reply):
    if reply.kind == zenoh.Z_STORAGE_DATA:
        replies.append((reply.rname, reply.data))
    elif reply.kind == zenoh.Z_REPLY_FINAL:
        replies_mvar.put(replies)


class ClientTest(unittest.TestCase):
    def client_test(self):
        global replies
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
        self.assertEqual(2, len(replies))
        self.assertEqual(sent_res, replies[0])
        self.assertEqual(sent_res, replies[1])
        replies = []

        z2.query("/test/python/client/**", "", reply_handler)
        replies_mvar.get()
        self.assertEqual(2, len(replies))
        self.assertEqual(sent_res, replies[0])
        self.assertEqual(sent_res, replies[1])
        replies = []

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
        self.assertEqual(2, len(replies))
        self.assertEqual(sent_res, replies[0])
        self.assertEqual(sent_res, replies[1])
        replies = []

        z2.query("/test/python/client/**", "", reply_handler)
        replies_mvar.get()
        self.assertEqual(2, len(replies))
        self.assertEqual(sent_res, replies[0])
        self.assertEqual(sent_res, replies[1])
        replies = []

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
        self.assertEqual(2, len(replies))
        self.assertEqual(sent_res, replies[0])
        self.assertEqual(sent_res, replies[1])
        replies = []

        z2.query("/test/python/client/**", "", reply_handler)
        replies_mvar.get()
        self.assertEqual(2, len(replies))
        self.assertEqual(sent_res, replies[0])
        self.assertEqual(sent_res, replies[1])
        replies = []

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
        self.assertEqual(2, len(replies))
        self.assertEqual(sent_res, replies[0])
        self.assertEqual(sent_res, replies[1])
        replies = []

        z2.query("/test/python/client/**", "", reply_handler)
        replies_mvar.get()
        self.assertEqual(2, len(replies))
        self.assertEqual(sent_res, replies[0])
        self.assertEqual(sent_res, replies[1])
        replies = []

        z1.undeclare_subscriber(z1_sub1)
        z2.undeclare_subscriber(z2_sub1)
        z1.undeclare_storage(z1_sto1)
        z2.undeclare_storage(z2_sto1)
        z1.undeclare_publisher(z1_pub1)
        z2.undeclare_publisher(z2_pub1)

        z1.close()
        z2.close()

        time.sleep(1)  # let time for close msg to comme back from router

        self.assertFalse(z1.running)
        self.assertFalse(z2.running)
