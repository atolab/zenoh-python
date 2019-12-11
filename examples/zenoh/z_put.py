import sys
from zenoh import Zenoh, Selector, Path, Workspace, Encoding, Value

# If not specified as 1st argument, use a relative path
# (to the workspace below): 'zenoh-python-put'
path = 'zenoh-python-put'
if len(sys.argv) > 1:
    path = sys.argv[1]

value = 'Put from Zenoh Python!'
if len(sys.argv) > 2:
    value = sys.argv[2]

locator = None
if len(sys.argv) > 3:
    locator = sys.argv[3]

print('Login to Zenoh (locator={})...'.format(locator))
z = Zenoh.login(locator)

print('Use Workspace on "/demo/example"')
w = z.workspace('/demo/example')

print('Put on {} : {}'.format(path, value))
w.put(path, Value(value, encoding=Encoding.STRING))

z.logout()
