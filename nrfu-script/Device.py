import Passwords

DEVICE_BASE = {
	'device_type' : 'cisco_ios',
	'username' : Passwords.USERNAME,
	'password' : Passwords.PASSWORD,
	'secret' : Passwords.SECRET,
}

class Device(object):
	def __init__(self, name, ip, tests):
		self.name = name
		self.sshParams = dict(DEVICE_BASE)
		self.sshParams.update({ 'ip' : ip })
		self.tests = tests

	def __str__(self):
		return "%s(%s): (%s)" % (self.name, self.sshParams['ip'], self.sshParams['device_type'])