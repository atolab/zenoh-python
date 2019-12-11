import sys
from zenoh import Zenoh, Selector, Path, Workspace, Encoding, Value

# If not specified as 1st argument, use a relative path
# (to the workspace below): 'zenoh-python-put'
path = 'zenoh-python-put'
if len(sys.argv) > 1:
    path = sys.argv[1]

locator = None
if len(sys.argv) > 2:
    locator = sys.argv[2]

print('Login to Zenoh (locator={})...'.format(locator))
z = Zenoh.login(locator)

print('Use Workspace on "/demo/example"')
w = z.workspace('/demo/example')

print('Remove {}'.format(path))
w.remove(path)

z.logout()
