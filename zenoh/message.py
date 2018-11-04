class Property(object):
    def __init__(self, key, value):
        self.key = key
        self.value = value        

class Message(object):
    VERSION = 0x01
    # Message Id
    SCOUT = 0x01
    HELLO = 0x02

    OPEN = 0x03
    ACCEPT = 0x04
    CLOSE = 0x05

    DECLARE = 0x06

    SDATA = 0x07
    BDATA = 0x08
    WDATA = 0x09

    QUERY = 0x0a
    PULL = 0x0b

    PING_PONG = 0x0c

    SYNCH = 0x0e
    ACK_NACK = 0x0f
    KEE_PALIVE = 0x10
    CONDUIT_CLOSE = 0x11
    FRAGMENT = 0x12
    RSPACE = 0x18
    MIGRATE = 0x14
    SDELTA_DATA = 0x15
    BDELTA_DATA = 0x16
    WDELTA_DATA = 0x17
    
    def __init__(self, mid):
        self.mid = mid
        self.version = Message.VERSION

class Header(Message):
    S_FLAG = 0x20
    M_FLAG = 0x20
    P_FLAG = 0x20

    R_FLAG = 0x40
    N_FLAG = 0x40
    C_FLAG = 0x40

    A_FLAG = 0x80
    U_FLAG = 0x80

    Z_FLAG = 0x80
    H_FLAG = 0x40
    L_FLAG = 0x20

    G_FLAG = 0x80
    I_FLAG = 0x20
    F_FLAG = 0x80
    O_FLAG = 0x20
    MID_MASK = 0x1f
    FLAGS_MASK = 0xe0

    @staticmethod
    def has_flag(h, f):    
        return h & f != 0
    
    @staticmethod
    def get_mid(h):
        return h & Header.MID_MASK

    @staticmethod
    def get_flags(h):
        return h & Header.FLAGS_MASK

    def __init__(self, flags, mid):
        super(Header, self).__init__(mid)
        self.flags = flags        
        self.header = self.flags | self.mid        

class ReliableHeader(Header):
    def __init__(self, flags, mid, sn):
        super(ReliableHeader, self).__init__(flags, mid)
        self.sn = sn
    
class Scout(Header):
    
    SCOUT_BROKER = 0x01
    SCOUT_DURABILITY = 0x02
    SCOUT_PEER = 0x04
    SCOUT_CLIENT = 0x08 
    
    def __init__(self, mask, properties=[]):        
        if len(properties) == 0:
            super(Scout, self).__init__(0, Message.SCOUT)
        else:
            super(Scout, self).__init__( Header.P_FLAG, Message.SCOUT)
        self.mask = mask
        self.properties = properties

    @staticmethod
    def scout_broker(properties=[]):
        return Scout(Scout.SCOUT_BROKER, properties)

class Open(Header):
    def __init__(self, pid, lease, locators=[], properties=[]):
        if len(properties) == 0:
            super(Open, self).__init__(0, Message.OPEN)
        else:
            super(Open, self).__init__( Header.P_FLAG, Message.OPEN)
        
        self.pid = pid
        self.lease = lease
        self.locators = locators
        self.properties = properties

class Accept(Header):
    def __init__(self, opid, apid, lease, properties=[]):
        if len(properties) == 0:
            super(Accept, self).__init__(0, Message.ACCEPT)
        else:
            super(Accept, self).__init__(Header.P_FLAG, Message.ACCEPT)
        self.opid = opid
        self.apid = apid
        self.lease = lease
        self.properties = properties

class Close(Header):
    def __init__(self,  pid, reason):
        super(Close, self).__init__(0, Message.CLOSE)
        self.pid = pid
        self.reason = reason 

class Declaration(Header):
    RESOURCE =  0x01
    PUBLISHER =  0x02
    SUBSCRIBER =  0x03
    SELECTION =  0x04
    BINDING =  0x05
    COMMIT =  0x06
    RESULT =  0x07
    FORGET_RES =  0x08
    FORGET_PUB =  0x09
    FORGET_SUB =  0x0a
    FORGET_SEL =  0x0b
    
    def __init__(self, flags, did):
        super(Declaration, self).__init__(flags, did)

class ResourceDecl(Declaration):
    def __init__(self, rid, rname, properties=[]):
        if len(properties) == 0:
            super(ResourceDecl, self).__init__(0, Declaration.RESOURCE)
        else:
            super(ResourceDecl, self).__init__(Header.P_FLAG, Declaration.RESOURCE)
        self.rid = rid 
        self.rname = rname
        self.properties = properties           

class SelectionDecl(Declaration):
    def __init__(self, sid, query, properties=[]):
        if len(properties) == 0:
            super(SelectionDecl, self).__init__(0, Declaration.SELECTION)
        else:
            super(SelectionDecl, self).__init__(Header.P_FLAG, Declaration.SELECTION)
    
        self.sid = sid
        self.query = query 
        self.properties = properties
        
class PublisherDecl(Declaration):
    def __init__(self, rid, properties=[]):
        if len(properties) == 0:
            super(PublisherDecl, self).__init__(0, Declaration.PUBLISHER)
        else:
            super(PublisherDecl, self).__init__(Header.P_FLAG, Declaration.PUBLISHER)
        self.rid = rid         
        self.properties = properties           

class SubscriptionMode(object):
    PUSH = 0x01
    PULL = 0x02
    # PERIODIC_PUSH = 0x03
    # PERIODIC_PULL = 0x04
    def __init__(self, id):
        self.id = id

class PushSubMode(SubscriptionMode):
    def __init__(self):
        super(PushSubMode, self).__init__(SubscriptionMode.PUSH)

# @TODO: Add remaining modes

class SubdcriberDecl(Declaration):
    def __init__(self, rid, mode, properties=[]):
        if len(properties) == 0:
            super(SubdcriberDecl, self).__init__(0, Declaration.SUBSCRIBER)
        else:
            super(SubdcriberDecl, self).__init__(Header.P_FLAG, Declaration.SUBSCRIBER)
        self.rid = rid 
        self.mode = mode
        self.properties = properties           

    @staticmethod
    def push_subscriber_decl(rid, properties=[]):
        return SubdcriberDecl(rid, PushSubMode(), properties)

class CommitDecl(Declaration):
    def __init__(self, commit_id):
        super(CommitDecl, self).__init__(0, Declaration.COMMIT)
        self.commit_id = commit_id

class ResultDecl(Declaration):
    def __init__(self, commit_id, status, id=None):
        super(ResultDecl, self).__init__(0, Declaration.RESULT)
        self.commit_id = commit_id        
        self.status = status
        self.id = id

class ForgetDecl(Declaration):
    def __init__(self, kind, id):
        super(ForgetDecl, self).__init__(0, kind)
        self.id = id

    @staticmethod
    def res(id):
        return ForgetDecl(Declaration.FORGET_RES, id)
    
    @staticmethod
    def pub(id):
        return ForgetDecl(Declaration.FORGET_PUB, id)    
    
    @staticmethod
    def sub(id):
        return ForgetDecl(Declaration.FORGET_SUB, id)  

    @staticmethod
    def sel(id):
        return ForgetDecl(Declaration.FORGET_SEL, id)    

class Declare(ReliableHeader):
    def __init__(self, flags, sn, declarations):
        super(Declare, self).__init__(flags, Message.DECLARE, sn)        
        self.declarations = declarations


class StreamData(ReliableHeader):
    def __init__(self, flags, sn, rid, payload, prid=None):
        super(StreamData, self).__init__(flags, Message.SDATA, sn)
        self.sn = sn
        self.rid = rid
        self.payload = payload
        self.prid = prid

class WriteData(ReliableHeader):
    def __init__(self, flags, sn, rname, payload):
        super(WriteData, self).__init__(flags, Message.WDATA, sn)
        self.rname = rname
        self.payload = payload



