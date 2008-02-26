#!/usr/bin/env python
## begin license ##
#
#    "Sahara" consists of two subsystems, namely an OAI-harvester and a web-control panel.
#    "Sahara" is developed for SURFnet by:
#        Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2006,2007 SURFnet B.V. http://www.surfnet.nl
#
#    This file is part of "Sahara"
#
#    "Sahara" is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    "Sahara" is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with "Sahara"; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##
#
import sys, os
if sys.version_info[:2] == (2,3):
	from sets import Set as set

def idfilename(logpath, name):
	return os.path.join(logpath, name + '.ids')

class Ids:
	def __init__(self, logpath, name):
		self._filename = idfilename(logpath,name)
		self._ids = set(map(lambda f:f.strip(), open(self._filename, 'a+').readlines()))
		self._idsfile = open(self._filename, 'a')
		
	def total(self):
		return len(self._ids)
	
	def clear(self):
		self._ids = []
		
	def close(self):
		self._idsfile.close()
		idfilenew = open(self._filename + '.new', 'w')
		try:
			for anId in self._ids:
				idfilenew.write( anId + '\n')
		finally:
			idfilenew.close()
		os.rename(self._filename + '.new', self._filename)

	def add(self, uploadid):
		self._ids.add(uploadid)
		self._idsfile.write( uploadid + '\n')
		self._idsfile.flush()

	def remove(self, uploadid):
		uploadid in self._ids and self._ids.remove(uploadid)
		