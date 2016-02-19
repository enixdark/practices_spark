#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import io
import os

class IO_json(object):
	def __init__(self, filepath, filename, filesuffix='json'):
		self.filepath = filepath
		self.filename = filename
		self.filesuffix = filesuffix

	def save(self,data):
		_file = "{0}/{1}.{2}".format(self.filepath,self.filename,self.filesuffix)
		mode = 'a' if os.path.isfile(_file) else 'w'
		with io.open(_file, mode, encoding='utf-8') as f:
			f.write(unicode(json.dumps(data, ensure_ascii= False)))

	def load(self):
		_file = "{0}/{1}.{2}".format(self.filepath,self.filename,self.filesuffix)
		with io.open(_file, encoding='utf-8') as f:
			return f.read()