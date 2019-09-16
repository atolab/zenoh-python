import sys
import time
import zenoh


def listener(rname, data, info):
    print(">> [Subscription listener] Received ('{}': '{}')"
          .format(rname, data.decode("utf-8")))


if __name__ == '__main__':
    locator = "tcp/127.0.0.1:7447"
    if len(sys.argv) > 1:
        locator = sys.argv[1]

    uri = "/demo/example/**"
    if len(sys.argv) > 2:
        uri = sys.argv[2]

    print("Connecting to {}...".format(locator))
    z = zenoh.Zenoh(locator, 'user', 'password')

    print("Declaring Subscriber on '{}'".format(uri))
    sub = z.declare_subscriber(uri, zenoh.SubscriberMode.push(), listener)

    while True:
        time.sleep(60)

    z.undeclare_subscriber(sub)
    z.close()
