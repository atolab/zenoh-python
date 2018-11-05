# This file contains all message codec necessary
# for the client. Notice that it does not necessarily 
# provide both encoder and decored for all messages since 
# in some cases messages will either only be sent or only received.

from .message import *
import logging

def foo():
    _ = Message(0)
    _ = Open([], 0, [],[])
    _ = ResourceDecl(0, '', [])    
    _ = PublisherDecl(0, [])
    _ = SubscriptionMode(PushSubMode)
    _ = Declare(0, 0, [])
    _ = SubdcriberDecl(0, PushSubMode.PUSH)
    _ = CommitDecl(0)

def encode_property(buf, p):
    buf.put_vle(p.key)
    buf.put_bytes(p.value)    

def decode_property(buf):
    k = buf.get_vle()
    v = buf.get_bytes()
    return Property(k,v)


def encode_sequence(buf, xs, encoder):
    buf.put_vle(len(xs))
    for x in xs:
        encoder(buf, x)

def  decode_sequence(buf, decoder):    
    n = buf.get_vle()    
    xs = []
    for _ in range(0, n):
        xs.append(decoder(buf))
    return xs

def encode_properties(buf, ps):
    if len(ps) != 0:    
        encode_sequence(buf, ps, encode_property)

def decode_properties(buf, h):
    properties = []
    if Header.has_flag(h, Header.P_FLAG):
        properties = decode_sequence(buf, decode_property)
    return properties    

def encode_scout(buf, m):
    buf.put(m.header)
    buf.put_vle(m.mask)
    if m.properties is not None:
        encode_sequence(buf, m.properties, encode_property)

def decode_scout(buf, header):    
    mask = buf.get_vle()
    properties = decode_properties(buf, header)    
    return Scout(mask, properties)
    
def encode_open(buf, m):
    buf.put(m.header)
    buf.put(m.version)
    buf.put_bytes(m.pid)
    buf.put_vle(m.lease)
    encode_sequence(buf, m.locators, buf.put_string)
    encode_properties(buf, m.properties)

def decode_accept(buf, header):    
    oid = buf.get_bytes()    
    aid = buf.get_bytes()    
    lease = buf.get_vle()    
    properties = decode_properties(buf, header)    
    return Accept(oid, aid, lease, properties)

def encode_close(buf, m):
    buf.put(m.header)
    buf.put_bytes(m.pid)
    buf.put(m.reason)

def decode_close(buf):
    pid = buf.get_bytes()
    reason = buf.get()
    return Close(pid, reason)

def encode_resource_decl(buf, d): 
    buf.put(d.header)
    buf.put_vle(d.rid)
    buf.put_string(d.rname)
    encode_properties(buf, d.properties)    

def decode_resource_decl(buf, h):
    rid = buf.get_vle()    
    rname = buf.get_string()
    properties = decode_properties(buf, h) 
    return ResourceDecl(rid, rname, properties) 
        
def encode_pub_decl(buf, d):
    buf.put(d.header)
    buf.put_vle(d.rid)
    encode_properties(buf, d.properties)        

def decode_pub_decl(buf, h):
    rid = buf.get_vle()
    properties = decode_properties(buf, h)
    PublisherDecl(rid, properties)

# TODO: 
#   The subscriber mode needs to be completed to allow
#   for the periodic subscription modes    
def encode_sub_mode(buf, mode):
    buf.put(mode.id)

def decode_sub_mode(buf):
    mid = buf.get()    
    return SubscriptionMode(mid)

def encode_sub_decl(buf, d):
    buf.put(d.header)    
    buf.put_vle(d.rid)
    encode_sub_mode(buf, d.mode)
    encode_properties(buf, d.properties)    

def decode_sub_decl(buf, h):
    rid = buf.get_vle()
    mode = decode_sub_mode(buf)
    ps = decode_properties(buf, h)
    return SubdcriberDecl(rid, mode, ps)

def encode_commit_decl(buf, d):
    buf.put(d.header)
    buf.put(d.commit_id)

def decode_commit_decl(buf, h):
    cid = buf.get()
    return CommitDecl(cid)

def encode_result_decl(buf, d):
    buf.put(d.h)
    buf.put(d.commit_id)
    buf.put(d.status)
    if d.id is not None:
        buf.put_vle(d.id)

def decode_result_decl(buf, h):
    commit_id = buf.get()
    status = buf.get()
    id = None
    if status != 0:
        id = buf.get_vle()
    return ResultDecl(commit_id, status, id)

def encode_forget_decl(buf, d):
    buf.put(d.header)
    buf.put_vle(d.id)

def decode_forget_decl(buf, h):
    id = buf.get_vle()
    return ForgetDecl(Header.get_mid(h), id)


def encode_declaration(buf, d):
    {
        Declaration.RESOURCE : lambda d : encode_resource_decl(buf, d),
        Declaration.PUBLISHER : lambda d : encode_pub_decl(buf, d),            
        Declaration.SUBSCRIBER : lambda d : encode_sub_decl(buf, d),   
        Declaration.COMMIT : lambda d : encode_commit_decl(buf, d),
        Declaration.RESULT : lambda d : encode_result_decl (buf, d),
        Declaration.FORGET_PUB : lambda d : encode_forget_decl(buf, d),
        Declaration.FORGET_SUB : lambda d : encode_forget_decl(buf, d),
        Declaration.FORGET_RES : lambda d : encode_forget_decl(buf, d),
        Declaration.FORGET_SEL : lambda d : encode_forget_decl(buf, d)
    }.get(d.mid)(d)    

def decode_declaration(buf):
    h = buf.get()
    id = Header.get_mid(h)
    decoder = {
        Declaration.RESOURCE : lambda buf,h : decode_resource_decl(buf, h),
        Declaration.PUBLISHER : lambda buf,h: decode_pub_decl(buf, h),            
        Declaration.SUBSCRIBER : lambda buf,h : decode_sub_decl(buf, h),   
        Declaration.COMMIT : lambda buf,h : decode_commit_decl(buf, h),
        Declaration.RESULT : lambda buf,h : decode_result_decl (buf, h),
        Declaration.FORGET_PUB : lambda buf,h : decode_forget_decl(buf, h),
        Declaration.FORGET_SUB : lambda buf,h : decode_forget_decl(buf, h),
        Declaration.FORGET_RES : lambda buf,h : decode_forget_decl(buf, h),
        Declaration.FORGET_SEL : lambda buf,h : decode_forget_decl(buf, h)        
    }.get(id)  
    decl = None  
    if decoder is not None: 
        return decoder(buf, h)
    else:
        raise 'Unsupported declaration {}'.format(id)

    return decl
    
def encode_declare(buf, m):
    buf.put(m.header)
    buf.put_vle(m.sn)
    encode_sequence(buf, m.declarations, encode_declaration)

def decode_declare(buf, h):
    sn = buf.get_vle()
    ds = decode_sequence(buf, decode_declaration)
    return Declare(Header.get_flags(h), sn, ds)

def encode_sdata(buf, m):
    buf.put(m.header)
    buf.put_vle(m.sn)
    buf.put_vle(m.rid)
    if m.prid is not None:
        buf.put_vle(m.prid)    
    buf.put_bytes(m.payload)

def decode_sdata(buf, h):
    sn = buf.get_vle()
    rid = buf.get_vle()
    prid = None
    if Header.has_flag(h, Header.A_FLAG):
        prid = buf.get_vle()
    payload = buf.get_bytes()
    return StreamData(Header.get_flags(h), sn, rid, payload, prid)

def encode_wdata(buf, m):
    buf.put(m.header)
    buf.put_vle(m.sn)
    buf.put_string(m.rname)
    buf.pub_bytes(m.payload)

def decode_wdata(buf, h):
    sn = buf.get_vle()
    rname = buf.get_string()
    payload = buf.get_bytes()
    return WriteData(Header.get_flags(h), sn, rname, payload)

def encode_message(buf, m):
    {
        Message.SCOUT : lambda buf,m : encode_scout(buf, m),
        Message.OPEN : lambda buf,m : encode_open(buf, m),
        Message.DECLARE : lambda buf,m : encode_declare(buf, m),
        Message.SDATA : lambda buf,m : encode_sdata(buf, m),
        Message.WDATA : lambda buf,m : encode_wdata(buf, m)
    }.get(m.mid)(buf,m) 

def decode_message(buf):
    h = buf.get()
    mid = Header.get_mid(h)
    decoder = {
        Message.SCOUT : lambda buf,h : decode_scout(buf, h),
        Message.ACCEPT : lambda buf,h : decode_accept(buf, h),
        Message.DECLARE : lambda buf,h : decode_declare(buf, h),
        Message.SDATA : lambda buf,h : decode_sdata(buf, h),
        Message.WDATA : lambda buf,h : decode_wdata(buf, h)
    }.get(mid, None)

    if decoder is None:
        logging.getLogger('io.zenoh').warning(">>> Received unexpected message {} -- ignoring.".format)
        return None
    else:
        return decoder(buf, h)
    

