import numpy as np 
from classBACNet import classBACNet
import pandas as pd 

BACNet_typedict = {'AI':0,'AO':1,'AV':2,'BI':3,'BO':4,'BV':5}
BACNet_typename = ['AI','AO','AV','BI','BO','BV']

class classBACobj:
	def __init__(self, **kwargs):
		if len(kwargs) < 1:
			print('ERROR: Please input something ...')
			return
		if not 'bacnet' in kwargs:
			print('Need classBACNet as \'bacnet=xxx\' ')
			return
		if not 'devid' in kwargs:
			print('ERROR: put device instance in the form of \'devid=###\'')
			return
		if not 'objid' in kwargs:
			print('ERROR: put object instance in the form of \'objid=###\'')
			return
		if not 'objtp' in kwargs:
			print('ERROR: put object type in the form of \'objtp=###\'')
			return
		if not 'prior' in kwargs:
			print('ERROR: put priority in the form of \'prior=###\'')
			return
		if not 'verbose' in kwargs:
			self.verb = 0
		else:
			self.verb = kwargs['verbose']

		self.bacnet = kwargs['bacnet']
		self.devid  = kwargs['devid']
		self.objid  = kwargs['objid']
		self.objtp  = kwargs['objtp']
		self.prior  = kwargs['prior']

	def write(self,**kwargs):
		if len(kwargs) < 1:
			print('ERROR: Please input something ...')
			return
		if not 'value' in kwargs:		
			print('ERROR: value is required')
			return
		if 'prior' in kwargs:
			prior = kwargs['prior']
		else:
			prior = self.prior
		self.bacnet.write(devid = self.devid, objtp = self.objtp, \
						  objid = self.objid, prior = prior, value = kwargs['value'])
		return
	
	def read(self,**kwargs):
		return self.bacnet.read(devid = self.devid, objtp = self.objtp, objid = self.objid)

	def readPrior(self,**kwargs):
		if 'prior' in kwargs:
			prior = kwargs['prior']
		else:
			prior = self.prior

		return self.bacnet.readplist(devid = self.devid, objtp = self.objtp, objid = self.objid, index = prior)

	def getInfoInString(self):
		return "DevID:{} {}{}".format(self.devid, BACNet_typename[self.objtp], self.objid  )

	def getinfo(self):
		print('BACobj info:')
		print('bacnet  : {0}'.format(self.bacnet))
		print('DevID   : {0}'.format(self.devid))
		print('ObjID   : {0}'.format(self.objid))
		print('ObjType : {0}'.format(self.objtp))
		print('Prior   : {0}'.format(self.prior))
		return

class classBACdev:
#
# 	devid: -> dict(objid) -> dict(type, name, val)
#
#
#
	def __init__(self, **kwargs):
		if not 'devid' in kwargs:
			print('ERROR: put device instance in the form of \'devid=###\'')
			return
		self.devid = kwargs['devid']		
		if not 'bacnet' in kwargs:
			print('Need classBACNet as \'bacnet=xxx\' ')
			return
		self.bacnet = kwargs['bacnet']
		self.devdict = {}
		self.objlist = []
		self.namelist = []
		self.magicChar = ':'
		return

	def importObj(self, **kwargs):
		if not 'objid' in kwargs:
			print('ERROR: put object type in the form of \'objid=###\'')
			return
		if not 'objtp' in kwargs:
			print('ERROR: put object type in the form of \'objtp=###\'')
			return
		if not 'name' in kwargs:
			print('ERROR: put object type in the form of \'name=###\'')
			return
		self.objlist = self.objlist + [str(kwargs['objid'])]
		self.devdict[str(kwargs['objid'])] = {}
		self.devdict[str(kwargs['objid'])]['name'] = kwargs['name']
		self.devdict[str(kwargs['objid'])]['val']  = []
		self.devdict[str(kwargs['objid'])]['type'] = kwargs['objtp']
		self.namelist = self.namelist + [str(kwargs['name'])]
		return

	def read(self):
		try:
			self.bacnet.readm(devdict=self.devdict,devid=self.devid)
		except ValueError:
			# device not support multiple rea, read one by one
			print('dev {} does not support multi-read'.format(self.devid))
			for obj in self.devdict:
				self.devdict[obj]['val'] = self.bacnet.read(devid=self.devid,\
															objid=obj,\
															objtp=self.devdict[obj]['type'])
		return
	def display(self):
		for obj in self.devdict:
			print('Dev {} value is {:1.f}'.format( self.devdict[obj]['name'], self.devdict[obj]['val'] ))

	def to_pd(self):
		df = pd.DataFrame(index=[0], columns = self.namelist)
		for obj in self.devdict:
			# self.df.at[0,'timestamp'] = nowtime
			# df.set_value(0,[self.devdict[obj]['name']],self.devdict[obj]['val'])
			df.at[0,self.devdict[obj]['name']] = self.devdict[obj]['val']
		return df.copy()

