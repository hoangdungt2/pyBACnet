import subprocess as sp
import shlex as sh 
import numpy  as np
import datetime, time, re, xlrd, os
import unicodedata
import cloudpickle
import copy

AI = 0
AO = 1
AV = 2
BO = 4
BV = 5
BV_ON   = 'active'
BV_OFF  = 'inactive'
nullVal = 'null'
errVal  = -9999
class classBACNet:
	def checkRet(self, retStr):
		tmp = retStr[0].decode("utf-8")
		tmp = tmp.replace('\n','')
		tmp = tmp.replace('\r','')	
		retVal = errVal	
		try:
			retVal = float(tmp)
		except Exception as e:
			if tmp.lower() == BV_ON:
				retVal = 1
			if tmp.lower() == BV_OFF:
				retVal = 0
			if tmp.lower() == nullVal:
				retVal = nullVal
		return retVal

	def __init__(self, **kwargs):
		if len(kwargs) < 1:
			print('ERROR: Please input something ...')
			return
		if not 'type' in kwargs:
			print('Need type = Ethernet or IP ')
			return
		if not 'os' in kwargs:
			print(' Need os = Linux or Windows')
			return
		if kwargs['os'].lower() == 'windows':
			self.prefix = ['.\\bin\\']
			if not 'adapt' in kwargs:
				print (' Need adapt as IP address')
				return
			bstr = ['set','BACNET_IFACE=' + kwargs['adapt']]
			p = sp.Popen(bstr,shell=True)
			p.communicate()
		elif kwargs['os'].lower() == 'linux':
			if not 'adapt' in kwargs:
				print (' Need adapt as eth#')
				return
			self.prefix = ['sudo','BACNET_IFACE='+str(kwargs['adapt']),'./bin/']
		else:
			print('ERROR: unsupported OS')
			return
		if not 'verbose' in kwargs:
			self.debug = 0
		else:
			self.debug = kwargs['verbose']
		return

	def readplist(self, **kwargs):
		if not 'devid' in kwargs:
			print('ERROR: put device instance in the form of \'devid=###\'')
			return
		if not 'objid' in kwargs:
			print('ERROR: put object instance in the form of \'objid=###\'')
			return
		if not 'objtp' in kwargs:
			print('ERROR: put object type in the form of \'objtp=###\'')
			return
		if not 'index' in kwargs:
			print('ERROR: put index in the form of \'objtp=index\'')
			return
		objtp = kwargs['objtp'] # object type, AI:0 AO:1 AV:2 BV:5
		objid = kwargs['objid'] # object instance
		devid = kwargs['devid'] # device instance
		index = kwargs['index'] # index
		# Usage: bacrp device-instance object-type object-instance property [index]
		tmpprefix = copy.deepcopy(self.prefix)
		tmpprefix[-1] += 'bacrp'
		bstr  = tmpprefix + [str(devid)] + [str(objtp)] + [str(objid)] + ['87'] + [str(index)]# assume it is always present value
		p   = sp.Popen(bstr,stdout=sp.PIPE)
		ret = p.communicate()
		return self.checkRet(ret)

	def readm(self, **kwargs):
		if not 'devdict' in kwargs:
			print('ERROR: put device instance in the form of \'devdict=###\'')
			return
		if not 'devid' in kwargs:
			print('ERROR: put device instance in the form of \'devid=###\'')
			return
		pDev = kwargs['devdict']
		bstr = [str(kwargs['devid'])]

		for obj in pDev:
			bstr = bstr + [str(pDev[obj]['type'])] + [obj] + ['85']
		
		tmpprefix = copy.deepcopy(self.prefix)
		tmpprefix[-1] += 'bacrpm'

		bstr = tmpprefix + bstr
		# print('COMMAND: {}'.format(bstr))
		p   = sp.Popen(bstr,stdout=sp.PIPE)
		ret = p.communicate()
		# print(ret)
		retstr = ret[0].decode('utf-8').splitlines()
		retstr = list(filter(None,retstr))
		# print(retstr)
		for line in retstr:
			# print(line)
			idx = line.find(':')
			# print('idx = {}'.format(idx))
			pDev[line[:idx]]['val'] = float(line[(idx+1):])
		return

	def read(self,**kwargs):
		if not 'devid' in kwargs:
			print('ERROR: put device instance in the form of \'devid=###\'')
			return
		if not 'objid' in kwargs:
			print('ERROR: put object instance in the form of \'objid=###\'')
			return
		if not 'objtp' in kwargs:
			print('ERROR: put object type in the form of \'objtp=###\'')
			return
		objtp = kwargs['objtp'] # object type, AI:0 AO:1 AV:2 BV:5
		objid = kwargs['objid'] # object instance
		devid = kwargs['devid'] # device instance
		# Usage: bacrp device-instance object-type object-instance property [index]
		tmpprefix = copy.deepcopy(self.prefix)
		tmpprefix[-1] += 'bacrp'
		bstr  = tmpprefix + [str(devid)] + [str(objtp)] + [str(objid)] + ['85'] # assume it is always present value
		p   = sp.Popen(bstr,stdout=sp.PIPE)
		ret = p.communicate()
		# if (objtp == BV) | (objtp == BO):
		# 	# for python3		
		# 	tmp = ret[0].decode("utf-8")
		# 	tmp = tmp.replace('\n','')
		# 	tmp = tmp.replace('\r','')
		# 	if (tmp == BV_ON):
		# 		retVal = 1
		# 	if (tmp == BV_OFF):
		# 		retVal = 0
		# else:
		retStr = ret[0].decode('utf-8')
		if (objtp == BV) | (objtp == BO):
			retVal = int(retStr.replace('\r','').replace('\n',''))
		else:
			retVal = float(retStr.replace('\r','').replace('\n',''))		
		return retVal

	def write(self,**kwargs):
		if not 'devid' in kwargs:
			print('ERROR: put device instance in the form of \'devid=###\'')
			return
		if not 'objid' in kwargs:
			print('ERROR: put object instance in the form of \'objid=###\'')
			return
		if not 'objtp' in kwargs:
			print('ERROR: put object type in the form of \'objtp=###\'')
			return
		if not 'value' in kwargs:
			print('ERROR: put value to write in the form of \'value=###\'  ')
			return
		if not 'prior' in kwargs:
			prior = 16 # default to be 16
		else:
			prior = kwargs['prior']

		objtp = kwargs['objtp'] # object type, AI:0 AO:1 AV:2 BV:5
		objid = kwargs['objid'] # object instance
		devid = kwargs['devid'] # device instance
		if type(kwargs['value']) == type('str'): #null
			value = 255
			value_tag = 0 #null value
		else:
			value = kwargs['value']
			value_tag = 4 #real data
		# Usage: bacwp device-instance object-type object-instance property priority index tag value [tag value...]
		tmpprefix = copy.deepcopy(self.prefix)
		tmpprefix[-1] += 'bacwp'
		bstr  = tmpprefix + [str(devid)] + [str(objtp)] + [str(objid)] + ['85'] + [str(prior)] + \
							  ['-1'] + [str(value_tag)] + [str(value)]
		if self.debug:
			print('COMMAND: ')
			print(bstr)
		p   = sp.Popen(bstr,stdout=sp.PIPE)
		ret = p.communicate()
		return
