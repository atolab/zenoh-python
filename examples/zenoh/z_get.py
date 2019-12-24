import sys
from zenoh import Zenoh, Selector, Path, Workspace, Encoding, Value

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

print('Get from {}'.format(selector))
for data in w.get(selector):
    print('  {} : {}'.format(data.path, data.value))


z.logout()
