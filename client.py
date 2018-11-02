from zenoh import *
import argparse
import socket 
from zenoh.converter import *
import array
import time 

ap = argparse.ArgumentParser()
ap.add_argument("-z", "--zenohd", required=True,
                help="ip:port for the zenoh broker")
args = vars(ap.parse_args())

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
    print('>> Reading frame of {} bytes'.format(flen))
    bs = sock.recv(flen)
    print('>> Received   {} bytes'.format(len(bs)))
    rbuf = IOBuf.from_bytes(bs)
    m = decode_message(rbuf)    
    print('>> Received message {}'.format(m.mid))
    return m 

def send_msg(sock, msg):
    buf = IOBuf()
    encode_message(buf, msg)
    # print('Open Messsage Hex Dump:\n')
    # buf.hex_dump()
    # print('--\n')
    lbuf = IOBuf(16)
    l = buf.write_pos
    lbuf.put_vle(l)
    sock.send(lbuf.get_raw_bytes())
    sock.send(buf.get_raw_bytes())

def recv_data(sock):
    while True:
        d = recv_msg(sock)
        print('>> Received data for resource {}'.format(d.rid))

def run_client(addr, port):
    
    s_sn = 0
    r_sn = -1
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    sock.setblocking(1)
    sock.connect((addr, port))
    buf = IOBuf()
    pid = array.array('B',[0,1,2,3,4,5,6,7])
        
    send_msg(sock, Open(pid, 0, [], []))    
    acpt = recv_msg(sock)    
    print('Received accept from {}'.format(acpt.apid))
    dres = ResourceDecl(21, '/home1')
    dsub = SubdcriberDecl(21, PushSubMode())
    commitId  = 0
    cmt = CommitDecl(commitId)
    send_msg(sock, Declare(0, s_sn, [dres, dsub, cmt]))
    
    m = recv_msg(sock)
    print('Received Message: {}'.format(m.mid))
    print('Starting Reveive Loop')
    recv_data(sock)


if __name__ == '__main__':
    ip,s,port = args['zenohd'].partition(':')
    run_client(ip, int(port))


