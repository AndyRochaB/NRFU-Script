#!/usr/bin/env python

from netmiko import ConnectHandler, NetMikoAuthenticationException, NetMikoTimeoutException
from datetime import datetime
from TestDevices import nrfuDevices
from distutils.util import strtobool
import multiprocessing
import logging
import os

MAX_RETRIES = 3
INVALID_COMMAND = "% Invalid input detected at '^' marker."
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'outputs')
os.path.dirname(os.path.abspath(__file__)) 


def createDir():

	if not os.path.exists(DIR):
		os.makedirs(DIR)
	

def runNRFU(device, multiprocessing = False, mpQueue = None):

	try:

		net_connect = ConnectHandler(**device.sshParams)
		net_connect.enable()	

		file = open(os.path.join(DIR, device.name + '.txt'), 'w')
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

		if multiprocessing:
			mpQueue.put(None)

		return None

	except (NetMikoTimeoutException, NetMikoAuthenticationException) as ex:

		logging.warning(device.name + ': ' + str(ex))
		
		if multiprocessing:
			mpQueue.put(device)

		return device

	except Exception as ex:

		logging.error(str(ex))

		if multiprocessing:
			mpQueue.put(device)

		return device

def main():

	failedDevices = []

	for device in nrfuDevices:
		if runNRFU(device):
			failedDevices.append(device)

	for tryN in range(0, MAX_RETRIES):
		if not failedDevices:
			print 'All tests finished!'
		
		else:
			tempFailDevices = []

			print 'Trying again (' + str(tryN + 1) + ')'
			
			for device in failedDevices:
				if runNRFU(device):
					tempFailDevices.append(device)
			
			failedDevices = tempFailDevices

	if failedDevices:
		print 'The following devices failed:'
		
		for device in sorted(failedDevices):
			print '\t* ' + str(device)

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

	for tryN in range(0, MAX_RETRIES):
		if not failedDevices:
			print 'All tests finished!'
		else:
			tempFailDevices = []
			processes = []
			mpQueue = multiprocessing.Queue()

			for device in failedDevices:

				p = multiprocessing.Process(target = runNRFU, args = (device, True, mpQueue,))

				processes.append(p)
				p.start()

			for p in processes:
				p.join()

			for p in processes:
				tempFailDevices.append(mpQueue.get())

			failedDevices = filter(None, tempFailDevices)

	if failedDevices:
		print 'The following devices failed:'
		
		for device in sorted(failedDevices):
			print '\t* ' + str(device)

	print '-----------------------------------------------------------------'
	print '|\t\t\t\t\t\t\t\t|'
	print '|\tAll tests ended at: ' + str(datetime.now()) + '\t\t|'
	print '|\t\t\t\t\t\t\t\t|'
	print '-----------------------------------------------------------------'

def scriptMode():

	print('Do you want to run the test on multiprocess mode? [yes/no]')
	
	while True:
		try:
			return strtobool(raw_input().lower())
	
		except ValueError:
			print('Please respond with "yes" or "no".')
	
	return False

if __name__ == '__main__':

	logging.basicConfig(filename='./nrfu.log', level=logging.INFO, format='%(asctime)s  %(levelname)s: %(message)s')
	logging.getLogger('paramiko').setLevel(logging.INFO)
	logging.info('Script started')

	createDir()
	
	mode = scriptMode()

	if mode:
		print 'Running in multiprocess mode'
		mainMultiProcess()
	else:
		print 'Running in single process mode'
		main()

	logging.info('Script endend')