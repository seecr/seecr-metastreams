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
#
import re, sys, os
from time import strptime
from datetime import datetime
NUMBERS_RE = re.compile(r'.*Harvested/Uploaded/Deleted/Total:\s*(\d+)/(\d+)/(\d+)/(\d+).*')
from itertools import imap, ifilter
from cgi import escape as escapeXml

def parseToTime(dateString):
	dateList = list((strptime(dateString.split(".")[0],"%Y-%m-%d %H:%M:%S"))[:6])
	dateList.append(int(dateString.split(".")[1][:3]) * 1000)
	date = datetime(*tuple(dateList))
	return date

def diffTime(newest, oldest):
	delta = newest - oldest
	return delta.seconds + delta.microseconds/1000000.0

class ThroughputReport:
	def __init__(self):
		self.records = 0
		self.seconds = 0.0
		
	def add(self, records, seconds):
		self.records += records
		self.seconds += seconds
		
	def recordsPerSecond(self):
		if self.seconds == 0.0:
			return '-'
		return  "%2.2f" % (self.records / self.seconds)
	
	def recordsPerDay(self):
		if self.seconds == 0.0:
			return '-'
		return "%2.0f" % (self.records / self.seconds * 24 * 3600)
	
	def hmsString(self):
		hours = int(self.seconds) / 3600
		minutes = int(self.seconds) % 3600 / 60
		seconds = int(self.seconds) % 60
		return "%02i:%02i:%02i" % (hours, minutes, seconds)

					
class ThroughputAnalyser:
	def __init__(self, eventpath):
		self.eventpath = eventpath
		
	def analyse(self, repositoryNames, dateSince):
		report = ThroughputReport()
		for name in repositoryNames:
			report.add(*self._analyseRepository(name, dateSince))
		return report
		
	def _analyseRepository(self, repositoryName, dateSince):
		events = open(os.path.join(self.eventpath, repositoryName + '.events'))
		records, seconds = 0, 0.0
		try:
			split = lambda l:map(str.strip, l.split('\t'))
			begintime = None
			datefilter = lambda (date, x,y,z): date[1:-1] >= dateSince 
			allevents = imap(split, ifilter(str.strip, events))
			for date, event, anIdentifier, comments in ifilter(datefilter, allevents):
				if event == "STARTHARVEST":
					begintime = parseToTime(date[1:-1])
					harvested = uploaded = deleted = total = -1
				elif event == 'ENDHARVEST':
					if begintime and harvested > -1:
						endtime = parseToTime(date[1:-1])
						if endtime > begintime:
							records += (int(uploaded) + int(deleted))
							seconds += diffTime(endtime, begintime)
							begintime = None
				elif event == 'SUCCES':
					match = NUMBERS_RE.match(comments)
					if match:
						harvested, uploaded, deleted, total = match.groups()
	
		finally:
			events.close()
		return records, seconds

if __name__ == '__main__':
	rs = Throughput()
	rs.main(sys.stdin, sys.stdout)