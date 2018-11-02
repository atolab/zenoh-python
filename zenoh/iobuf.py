import array 
from .converter import byte_to_int


class IOBufException(IOError):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return 'IOBufException: {}'.format(self.msg)
        

class IOBuf(object):
    DEFAULT_IOBUF_SIZE = 1024 * 64
    def __init__(self, capacity=None):
        self.read_pos = 0
        self.write_pos = 0
        if capacity is None:
            self.capacity = IOBuf.DEFAULT_IOBUF_SIZE
        else:
            self.capacity = capacity                
        self.limit = self.capacity
        self.buf = array.array('B', (0 for i in range(self.capacity)))

    @staticmethod 
    def from_bytes(bs):
        l = len(bs)
        b = IOBuf(l)        
        for i in range(0, l):
            b.put(byte_to_int([bs[i]]))
        b.write_pos = l
        return b

    def __str__(self):
        return 'IOBuf(read_pos:{}, write_pos:{}, capacity:{})'.format(self.read_pos,  self.write_pos, self.capacity)

    
    def hex_dump(self):
        for i in range(0, self.write_pos):
            print('0x{} '.format(self.buf[i]))
                

    def clear(self):
        self.read_pos = 0
        self.write_pos = 0
        self.limit = self.capacity

    def reset_read_pos(self):
        self.read_pos = 0

    def put(self, b):
        if self.write_pos < self.capacity:        
            self.buf[self.write_pos] = b
            self.write_pos += 1
        else:
            self.buf.extend(IOBuf())
            self.capacity += IOBuf.DEFAULT_IOBUF_SIZE
            self.put(b)
    
    def get(self):
        if self.read_pos < self.write_pos:
            v = self.buf[self.read_pos]
            self.read_pos += 1
            return v
        else:
             raise IOBufException('Cannot read beyond write position (read_pos : {}, write_pos: {})'.format(self.read_pos, self.write_pos))

    def put_vle(self, v):
        if v < 0x7f:            
            self.put(v)
        else:
            c = (v & 0x7f) | 0x80            
            r = v >> 7
            self.put(c)
            self.put_vle(r)

    def __extract_vle(self, cv, n):
        c = self.get()
        nv = ((c & 0x7f) << (7*n)) | cv
        if c > 0x7f:
            return self.__extract_vle(nv, n+1)
        else:
            return nv

    def get_vle(self):
        return self.__extract_vle(0,0)

    def put_bytes(self, bs):                
        l = len(bs) 
        self.put_vle(l)
        for i in range(0, l):
            self.buf[self.write_pos + i] = bs[i]
        self.write_pos += l

    def get_bytes(self):
        n = self.get_vle()
        bs = array.array('B')
        for i in range(0, n):
            bs.append(self.buf[self.read_pos + i])
        self.read_pos += n        
        return bs 

    def put_string(self, s):        
        self.put_bytes(s.encode())

    def get_string(self):        
        bs = self.get_bytes()
        return bs.tobytes().decode("utf-8")

    def get_raw_bytes(self):
        a = array.array('B')
        for i in range(0, self.write_pos):
            a.append(self.buf[self.read_pos + i])
        self.read_pos = self.write_pos
        return a.tobytes()




