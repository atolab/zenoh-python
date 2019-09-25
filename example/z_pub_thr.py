import sys
import zenoh

if __name__ == '__main__':
    locator = "tcp/127.0.0.1:7447"
    if len(sys.argv) < 2:
        print('USAGE:\n\tz_pub_thr <payload-size> [<zenoh-locator>]\n\n')
        sys.exit(-1)
    size = int(sys.argv[1])
    print("Running throughput test for payload of {} bytes".format(size))
    if len(sys.argv) > 2:
        locator = sys.argv[2]

    z = zenoh.Zenoh(locator, 'user', 'password')
    pub = z.declare_publisher('/test/thr')

    bs = bytearray()
    for i in range(0, size):
        bs.append(i % 10)

    while True:
        z.stream_data(pub, bytes(bs))

    z.close()
