#!/usr/bin/env python

from netmiko import ConnectHandler, NetMikoAuthenticationException, NetMikoTimeoutException
from datetime import datetime
from TestDevices import nrfuDevices
import multiprocessing

MAX_RETRIES = 3
INVALID_COMMAND = "% Invalid input detected at '^' marker."

def runNRFU(device, multiprocessing = False, mpQueue = None):

	try:

		net_connect = ConnectHandler(**device.sshParams)
		net_connect.enable()

		file = open(device.name + '.txt', 'w')
		beginTime = str(datetime.now())

		print ('Beginning tests for ' + device.name + ' at ' + beginTime)
		file.write('Beginning tests at ' + beginTime)

		for test in device.tests:	
			file.write('\n\n########################################\n')
			file.write('Beginning with ' + test['name'] + '\n')
			file.write('########################################\n')
			if not multiprocessing: print ('\tBeginning with ' + test['name'])

			for command in test['commands']:
				file.write('\n---------------' + command + '----------------\n')

				output = net_connect.send_command(command)

				if INVALID_COMMAND in output:
					file.write('\nCommand: "' + command + '" not recognized!\n')
					if not multiprocessing: print ('\tCommand: "' + command + '" not recognized!')

				else:
					file.write('\n' + output + '\n')

				file.write('\n--------------------------------------\n')

		endTime = str(datetime.now())

		print ('Tests for ' + device.name + ' ended at ' + endTime)
		if not multiprocessing: print ('--------------------------------------\n')

		file.write('Tests ended at ' + endTime)
		file.close()

		net_connect.send_command('exit')

	except (NetMikoTimeoutException, NetMikoAuthenticationException) as ex:

		print 'Warning!: ' + str(ex)
		
		if mpQueue:
			mpQueue.put(device)
		else:
			return device

	except Exception as ex:

		print str(ex)

		if mpQueue:
			mpQueue.put(device)
		else:
			return device

	if mpQueue:
		mpQueue.put(None)

	return None

def main():

	failedDevices = []

	for device in nrfuDevices:
		if runNRFU(device):
			failedDevices.append(device)

	for tryN in range(0, MAX_RETRIES):
		if not failedDevices:
			print 'All tests finished!'
			break
		
		else:
			tempFailDevices = []

			print 'Trying again (' + str(tryN + 1) + ')'
			
			for device in failedDevices:
				if runNRFU(device):
					tempFailDevices.append(device)
			
			failedDevices = tempFailDevices

	if failedDevices:
		print 'The following devices failed:'
		
		for device in failedDevices:
			print '\t* ' + device.name

def mainMultiProcess():

	mpQueue = multiprocessing.Queue()
	processes = []
	failedDevices = []

	print '-----------------------------------------------------------------'
	print '|\t\t\t\t\t\t\t\t|'
	print '|\tAll tests begin at: ' + str(datetime.now()) + '\t\t|'
	print '|\t\t\t\t\t\t\t\t|'
	print '-----------------------------------------------------------------'

	for device in nrfuDevices:

		p = multiprocessing.Process(target = runNRFU, args = (device, True, mpQueue,))

		processes.append(p)
		p.start()

	for p in processes:
		p.join()

	for p in processes:
		failedDevices.append(mpQueue.get())

	failedDevices = filter(None, failedDevices)

	mpQueue = multiprocessing.Queue()
	processes = []

	for tryN in range(0, MAX_RETRIES):
		if not failedDevices:
			print 'All tests finished!'
			break
		
		else:
			tempFailDevices = []

			print 'Trying again (' + str(tryN + 1) + ')'
			
			for device in failedDevices:

				p = multiprocessing.Process(target = runNRFU, args = (device, True, mpQueue,))

				processes.append(p)
				p.start()

				for p in processes:
					p.join()

				for p in processes:
					tempFailDevices.append(mpQueue.get())

			failedDevices = failedDevices = filter(None, tempFailDevices)

	if failedDevices:
		print 'The following devices failed:'
		
		for device in failedDevices:
			print '\t* ' + device.name

	print '-----------------------------------------------------------------'
	print '|\t\t\t\t\t\t\t\t|'
	print '|\tAll tests ended at: ' + str(datetime.now()) + '\t\t|'
	print '|\t\t\t\t\t\t\t\t|'
	print '-----------------------------------------------------------------'

if __name__ == '__main__':

	# Comment or uncomment in order to activate 'single process' or 'multiprocess' mode
	# main()
	# mainMultiProcess()
