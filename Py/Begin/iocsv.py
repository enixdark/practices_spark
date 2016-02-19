#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from collections import namedtuple
import csv
class IO_csv(object):

	def __init__(self, filepath, filename, filesuffix='csv'):
		self.filepath = filepath
		self.filename = filename
		self.filesuffix = filesuffix

	def save(self,data, NTname, fields):
		NTuple = namedtuple(NTname, fields)
		_file = "{0}/{1}.{2}".format(self.filepath,self.filename,self.filesuffix)
		mode = 'ab' if os.path.isfile(_file) else 'wb'
		with open(_file,mode) as f:
			writer = csv.writer(f)
			writer.writerow(fields)
			writer.writerows([row for row in map(NTuple._make,data)])

	def load(self,NTname, fields):
		NTuple = namedtuple(NTname, fields)
		_file = "{0}/{1}.{2}".format(self.filepath,self.filename,self.filesuffix)
		with open(_file,'rU') as f:
			reader = csv.reader(f)
			for row in map(NTuple._make, reader):
				yield row

fields01 = ['id', 'created_at',	'user_id', 'user_name',	'tweet_text',	
'url']
Tweet01	= namedtuple('Tweet01',fields01)

def	parse_tweet(data):
	"""
	Parse	a	``tweet``	from	the	given	response	data.
	"""
	return Tweet01(
		id=data.get('id', None),
		created_at=data.get('created_at', None),
		user_id=data.get('user_id',	None),
		user_name=data.get('user_name',	None),
		tweet_text=data.get('tweet_text',	None),
		url=data.get('url')
	)
