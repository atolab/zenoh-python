def int_to_byte(i):
    return i.to_bytes(1, byteorder='big')

def byte_to_int(b):
    return int.from_bytes(b, byteorder='big', signed=False)
