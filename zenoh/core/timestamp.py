from ctypes import *
import datetime
import binascii


# Timestamp
class Timestamp(Structure):
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
