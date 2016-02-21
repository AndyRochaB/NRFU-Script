#!/usr/bin/env python

from netmiko import ConnectHandler, NetMikoAuthenticationException, NetMikoTimeoutException
from datetime import datetime
from TestDevices import *

MAX_RETRIES = 3
INVALID_COMMAND = "% Invalid input detected at '^' marker."

def runNRFU(device):
	
	try:
	
		net_connect = ConnectHandler(**device.sshParams)
		net_connect.enable()
	
		file = open(device.name + '.txt', 'w')
		now = str(datetime.now())
	
		print 'Beginning tests for ' + device.name + ' at ' + now
		file.write('Beginning tests at ' + now)
	
		for test in device.tests:	
			file.write('\n\n########################################\n')
			file.write('Beginning with ' + test['name'] + '\n')
			file.write('########################################\n')
			print ('\tBeginning with ' + test['name'])
	
			for command in test['commands']:
				file.write('\n---------------' + command + '----------------\n')
	
				output = net_connect.send_command(command)
	
				if INVALID_COMMAND in output:
					file.write('\nCommand: "' + command + '" not recognized!\n')
					print '\tCommand: "' + command + '" not recognized!'
	
				else:
					file.write('\n' + output + '\n')
	
				file.write('\n--------------------------------------\n')
	
		now = str(datetime.now())
	
		print 'Tests ended at ' + now
		print '--------------------------------------\n'
	
		file.write('Tests ended at ' + now)
		file.close()
	
		net_connect.send_command('exit')
	
	except (NetMikoTimeoutException, NetMikoAuthenticationException) as ex:
	
		print 'Warning!:  ' + str(ex)
		return False

	except Exception as ex:
		print str(ex)

	
	return True
			 
def main():

	failedDevices = []

	for device in labDevices:
		if not runNRFU(device):
			failedDevices.append(device)

	for tryN in range(0, MAX_RETRIES):
		if not failedDevices:
			print 'All tests finished!'
			break
		
		else:
			tempFailDevices = []

			print 'Trying again (' + str(tryN + 1) + ')'
			
			for device in failedDevices:
				if not runNRFU(device):
					tempFailDevices.append(device)
			
			failedDevices = tempFailDevices

	if failedDevices:
		print 'The following devices failed:'
		
		for device in failedDevices:
			print '\t* ' + device.name

# def mainMultiProcess():

if __name__ == '__main__':
	main()