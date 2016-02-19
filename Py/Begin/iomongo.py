#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import	MongoClient


class IO_mongo(object):
	conn = {'host':'localhost', 'port':'27017'}

	def __init__(self, db='twtr_db', coll='twtr_coll',**conn):
		self.client	= MongoClient(**conn)
		self.db	= self.client[db]
		self.coll =	self.db[coll]

	def save(self,data):
		return self.coll.insert(data)

	def load(self, is_cursor=False, criteria=None,	projection=None):
		if criteria is None:
			criteria = {}

		cursor = self.coll.find(criteria,projection) if projection else self.coll.find(criteria)
		if is_cursor:
			return cursor
		else:
			return [item for item in cursor]


