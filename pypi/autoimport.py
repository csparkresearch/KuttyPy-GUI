######## AUTOMATIC INITIALIZATION ON IMPORT ####
# This package was installed from PyPi via pip
import inspect

KP=connect(autoscan=True)
if not KP.connected:
	print('kuttypy hardware not found. Check connections')
	sys.exit(0)

for a in dir(KP):
	attr = getattr(KP, a)
	if inspect.ismethod(attr) and a[:2]!='__':
		exec('''%s = attr'''%a)#kwargs[a] = attr
