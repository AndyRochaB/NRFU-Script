from Passwords import *

DEVICE_BASE = {
	'device_type' : 'cisco_ios',
	'username' : USERNAME,
	'password' : PASSWORD,
	'secret' : SECRET,
}

class Device(object):
	def __init__(self, name, ip, tests):
		self.name = name
		self.sshParams = dict(DEVICE_BASE)
		self.sshParams.update({ 'ip' : ip })
		self.tests = tests