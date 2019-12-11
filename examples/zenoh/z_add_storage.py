import sys
from zenoh import Zenoh, Selector, Path, Workspace, Encoding, Value

selector = '/demo/example/**'
if len(sys.argv) > 1:
    selector = sys.argv[1]

storage_id = 'Demo'
if len(sys.argv) > 2:
    storage_id = sys.argv[2]

locator = None
if len(sys.argv) > 3:
    locator = sys.argv[3]

print('Login to Zenoh (locator={})...'.format(locator))
z = Zenoh.login(locator)

a = z.admin()

print('Add storage {} with selector {}'.format(storage_id, selector))
properties = {'selector': selector}
a.add_storage(storage_id, properties)

z.logout()
