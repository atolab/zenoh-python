import sys
from zenoh import Zenoh, Selector, Path, Workspace
from zenoh import Change, ChangeKind, Encoding, Value

selector = '/demo/example/**'
if len(sys.argv) > 1:
    selector = sys.argv[1]

locator = None
if len(sys.argv) > 2:
    locator = sys.argv[2]

print('Login to Zenoh (locator={})...'.format(locator))
z = Zenoh.login(locator)

print('Use Workspace on "/"')
w = z.workspace('/')


def listener(changes):
    for change in changes:
        if change.get_kind() == ChangeKind.PUT:
            print('>> [Subscription listener] Received PUT on "{}": "{}"'
                  .format(change.get_path(), change.get_value()))
        elif change.get_kind() == ChangeKind.UPDATE:
            print('>> [Subscription listener] Received UPDATE on "{}": "{}"'
                  .format(change.get_path(), change.get_value()))
        elif change.get_kind() == ChangeKind.REMOVE:
            print('>> [Subscription listener] Received REMOVE on "{}"'
                  .format(change.get_path()))
        else:
            print('>> [Subscription listener] Received kind:"{}" on "{}"'
                  .format(change.get_kind(), change.get_path()))


print('Subscribe on {}'.format(selector))
subid = w.subscribe(selector, listener)

print('Enter \'q\' to quit...')
while sys.stdin.read(1) != 'q':
    pass

w.unsubscribe(subid)
z.logout()
