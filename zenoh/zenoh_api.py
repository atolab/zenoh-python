import socket 
import uuid
import os
from .message import Open
from .iobuf import *
from .codec import *
import threading
import logging
import sys

def get_frame_len(sock):
    buf = IOBuf()
    v = 0xff    
    while v > 0x7f:         
        b = sock.recv(1)
        v = byte_to_int(b)
        buf.put(v) 
    
    return buf.get_vle()

def recv_msg(sock):
    flen = get_frame_len(sock)
    bs = sock.recv(flen)
    rbuf = IOBuf.from_bytes(bs)
    m = decode_message(rbuf)        
    return m 

def send_msg(sock, msg):
    buf = IOBuf()
    encode_message(buf, msg)    
    lbuf = IOBuf(16)
    l = buf.write_pos
    lbuf.put_vle(l)
    sock.send(lbuf.get_raw_bytes())
    sock.send(buf.get_raw_bytes())

class Publisher(object):
    def __init__(self, rid, rname, z):
        self.rid = rid
        self.rname = rname
        self.zenoh = z
        self.matching = False
        self.on_matching_change = lambda b : b
    
    def set_matching(self, on):
        self.matching = on
        self.on_matching_change(on)

    def observe_matching(self, observer):
        self.on_matching_change = observer

    def write(self, data):
        if self.matching:
            self.zenoh.write_sdata(self.rid, data)
        
    def close(self):
        self.zenoh.forget_publisher(self.rid)
    

def get_log_level():
    l = logging.ERROR
    i = 0
    for a in sys.argv:
        if a.startswith('--log='):
            _,_,lvl = a.partition('=')
            l = getattr(logging, lvl.upper())
        elif a == '-l':
            l = getattr(logging, sys.argv[i+1].upper())        
        i +=1
    return l            
    
class Zenoh(threading.Thread):
    DEFAULT_SCOUT_ADDRESS = "239.255.0.1"
    DEFAULT_PORT = 7447
    DEFAULT_TIMEOUT = 5
    def __init__(self,  sock, client_id, broker_id, locator, on_close):
        threading.Thread.__init__(self)        
        self.pid = None
        self.locator = None 
        self.connected = True
        self.r_sn = -1
        self.s_sn_ = 0
        self.commit_id = 0
        self.sock = sock
        self.running = True
        self.subs = {}
        self.pubs = {}
        self.decls = {}
        self.on_close = on_close 
        self.next_rid_ = 2
        self.next_sid_ = 1
        self.res_map = {}
        self.logger = logging.getLogger('io.zenoh')
        self.log_level = get_log_level()
        self.logger.setLevel(self.log_level)        
        ch = logging.StreamHandler()
        ch.setLevel(self.log_level)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)        
        self.logger.addHandler(ch)
        
        
    def close(self):        
        self.on_close(self)
        self.running = False
        self.sock.close() 

    def next_rid(self):
        id = self.next_rid_
        self.next_rid_ += 2
        return id

    def next_sid(self):
        id = self.next_sid_
        self.next_sid_ += 1
        return id

    def next_s_sn(self):
        sn = self.s_sn_
        self.s_sn_ += 1
        return sn
    
    def next_commit_id(self):
        id = self.commit_id 
        self.commit_id += 1
        return id

    @staticmethod 
    def scout(locator):
        raise NotImplementedError()

    @staticmethod
    def connect(locator, on_close = lambda z : z , lease = 0):
        addr,_,p = locator.partition(':')
        if p == '':
            port = Zenoh.DEFAULT_PORT
        else:
            port = int(p)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.setblocking(1)
        sock.connect((addr, port))
        node_id = uuid.getnode()
        client_id = bytearray(int.to_bytes(node_id, 6, byteorder='big'))        
        pid = os.getpid()
        postfix = int.to_bytes(pid, 4, byteorder='big')
        for b in postfix:
            client_id.append(b)
        
        send_msg(sock, Open(client_id, 0, []))
        m = recv_msg(sock)
        z = None
        if m.mid == Message.ACCEPT:
            z = Zenoh(sock, client_id, m.apid, locator, on_close)
        elif m.mid == Message.CLOSE:
            raise 'Broker refused connection because of {}'.format(m.reason)
        else:
            raise 'Broker replied with unexpected message'
        
        z.start()
        return z

    def handle_other_msg(self, msg):
        self.logger.warning(' Received message {} -- ignoring'.format(msg.mid))
    
    def handle_sdata(self, msg):
        cs = self.subs.get(msg.rid, [])     
        for listener in cs:
            listener(msg.rid, msg.payload)
    
    def handle_wdata(self, msg):
        self.logger.warning('>> Received message {} -- ignoring'.format(msg.mid))
        
    def handle_close(self, msg): 
        self.logger.debug('>> handle_close')       
        self.on_close(self)
        self.running = False
        socket.close(self.sock)

    def handle_result_decl(self, d):
        self.logger.debug('>> handle_result_decl for cid: {}'.format(d.commit_id))
        cv = self.decls.get(d.commit_id, None)
        if cv != None:
            cv.notify()

    def handle_sub_decl(self, d):        
        self.logger.debug('>> handle_sub_decl for resource: {}'.format(d.rid))
        for s in self.pubs.get(d.rid, []):
            s.set_matching(True)

    def handle_forget_sub_decl(self, d):
        self.logger.debug('>> Forgetting subscrition for resource: {}'.format(d.id))
        for p in self.pubs.get(d.id, []):            
            p.set_matching(False)
            
    def handle_ignored_declaration(self, d):
        self.logger.debug('>> handle_ignored_declaration for declaration {}'.format(d.mid))

    def handle_declare(self, msg):
        other_case = self.handle_ignored_declaration
        for d in msg.declarations:             
            {                
                Declaration.RESULT : lambda d : self.handle_result_decl(d),
                Declaration.SUBSCRIBER : lambda d : self.handle_sub_decl(d),
                Declaration.FORGET_SUB : lambda d : self.handle_forget_sub_decl(d)
            }.get(d.mid, other_case)(d)           

    def run(self):                
        try:
            while self.running:                    
                m = recv_msg(self.sock)
                self.logger.debug('>> Received msg with id: {}'.format(m.mid))
                default_case = lambda msg : self.handle_other_msg(msg)
                {
                    Message.SDATA : lambda msg : self.handle_sdata(msg),
                    Message.WDATA : lambda msg : self.handle_wdata(msg),
                    Message.CLOSE : lambda msg : self.handle_close(msg),
                    Message.DECLARE : lambda msg : self.handle_declare(msg)
                }.get(m.mid, default_case)(m)
        except:
            e = sys.exc_info()[0]
            self.logger.debug('Terminating the runloop because of {}'.format(e))

    def register_resource(self, rname, rid):    
        if rid is None:
            rid = self.next_rid()
        self.res_map[rname] = rid
        self.logger.debug('>> Registered resurce: {} with id: {}'.format(rname, rid))
        return rid  

    def declare_resource(self, rname, rid=None):
        if self.res_map.get(rname) is None:
            r_rid = self.register_resource(rname, rid)        
            self.logger.debug('>> Declaring resurce: {} with id: {}'.format(rname, r_rid))
            dres = ResourceDecl(r_rid, rname)        
            cid = self.next_commit_id()
            cmt = CommitDecl(cid)                 
            send_msg(self.sock, Declare(0, self.next_s_sn(), [dres, cmt]))
    
    def declare_subscriber(self, rname, listener):
        ds = []
        rid = self.res_map.get(rname)
        if rid is None:
            rid = self.register_resource(rname, None)
            ds.append(ResourceDecl(rid, rname))
        self.logger.debug('>> Declaring subscriber for resource: {} with id: {}'.format(rname, rid))
        ds.append(SubdcriberDecl(rid, PushSubMode()))
        ds.append(CommitDecl(self.next_commit_id()))
        send_msg(self.sock, Declare(0, self.next_s_sn(), ds))
        cs = self.subs.get(rid,[])
        cs.append(listener)
        self.subs[rid] = cs
        return rid

    def declare_publisher(self, rname):
        ds = []
        rid = self.res_map.get(rname)
        if rid is None:
            rid = self.register_resource(rname, None)
            ds.append(ResourceDecl(rid, rname))
        self.logger.debug('>> Declaring publisher for resource: {} with id: {}'.format(rname, rid))    
        ds.append(PublisherDecl(rid))
        ds.append(CommitDecl(self.next_commit_id()))
        send_msg(self.sock, Declare(0, self.next_s_sn(), ds))
        pub = Publisher(rid, rname, self)
        ps = self.pubs.get(rid, [])
        ps.append(pub)
        self.pubs[rid] = ps
        return pub
        
    def forget_publisher(self, rid):        
        if self.pubs.get(rid) is not None:
            ds = []
            ds.append(ForgetDecl.sub(rid))
            ds.append(CommitDecl(self.next_commit_id()))
            send_msg(self.sock, Declare(0, self.next_s_sn(), ds))
            self.pubs[rid] = None

    def write_sdata(self, rid, data):
        m = StreamData(0, self.next_s_sn(),rid, data)
        send_msg(self.sock, m)

