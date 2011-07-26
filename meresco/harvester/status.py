## begin license ##
#
#    "Meresco Harvester" consists of two subsystems, namely an OAI-harvester and
#    a web-control panel.
#    "Meresco Harvester" is originally called "Sahara" and was developed for
#    SURFnet by:
#        Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2011 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2011 Stichting Kennisnet http://www.kennisnet.nl
#
#    This file is part of "Meresco Harvester"
#
#    "Meresco Harvester" is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    "Meresco Harvester" is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with "Meresco Harvester"; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from os.path import join, isfile, isdir
from os import listdir
from lxml.etree import parse
from xml.sax.saxutils import escape as escapeXml
from re import compile
from itertools import ifilter

NUMBERS_RE = compile(r'.*Harvested/Uploaded/Deleted/Total:\s*(\d+)/(\d+)/(\d+)/(\d+).*')

class Status(object):

    def __init__(self, logPath, statePath):
        self._logPath = logPath
        self._statePath = statePath

    def getStatus(self, domainId, repositoryIds):
        ignoredDir = join(self._logPath, domainId, "ignored")
        repositoryIds = [repositoryIds] if repositoryIds else []
        if not repositoryIds and isdir(ignoredDir):
            repositoryIds = listdir(ignoredDir)
        yield "<GetStatus>"
        for repoId in repositoryIds:
            yield self._getRepositoryStatus(domainId, repoId)
        yield "</GetStatus>"

    def ignoredRecords(self, domainId, repositoryId):
        ignoredFile = join(self._statePath, domainId, "%s_ignored.ids" % repositoryId)
        if not isfile(ignoredFile):
            return []
        return reversed([line.strip() for line in open(ignoredFile) if line.strip()])

    def getIgnoredRecord(self, domainId, repositoryId, recordId):
        return parse(open(join(self._logPath, domainId, "ignored", repositoryId, recordId)))

    def _getRepositoryStatus(self, domainId, repoId):
        stats = self._parseEventsFile(domainId, repoId)
        yield '<status repositoryId="%s">' % repoId
        yield '<lastHarvestDate>%s</lastHarvestDate>' % stats.get('lastHarvestDate', '')
        yield '<harvested>%s</harvested>' % stats.get('harvested', '')
        yield '<uploaded>%s</uploaded>' % stats.get('uploaded', '')
        yield '<deleted>%s</deleted>' % stats.get('deleted', '')
        yield '<total>%s</total>' % stats.get('total', '')
        yield '<totalerrors>%s</totalerrors>' % stats.get('totalerrors', '')
        yield '<recenterrors>'
        for error in stats['recenterrors']:
            yield '<error date="%s">%s</error>' % (error[0], escapeXml(error[1])) 
        yield '</recenterrors>'
        yield '<ignored>%s</ignored>' % self._ignoredCount(domainId, repoId)
        yield '</status>'

    def _ignoredCount(self, domainId, repositoryId):
        ignoredFile = join(self._statePath, domainId, "%s_ignored.ids" % repositoryId)
        return len(open(ignoredFile).readlines()) if isfile(ignoredFile) else 0

    def _parseEventsFile(self, domainId, repositoryId):
        parseState = {'errors': []}
        eventsfile = join(self._logPath, domainId, "%s.events" % repositoryId)
        if isfile(eventsfile):
            for line in open(eventsfile):
                stateLine = line.strip().split('\t')
                if len(stateLine) != 4:
                    continue
                date, event, id, comments = stateLine
                date = date[1:-1]
                if event == 'SUCCES':
                    _succes(parseState, date, comments)
                elif event == 'ERROR':
                    _error(parseState, date, comments)
        recenterrors = parseState["errors"][-10:]
        recenterrors.reverse()
        stats = {}
        for k,v in ifilter(lambda (k,v): k != 'errors', parseState.items()):
            stats[k] = v
        stats["totalerrors"] = len(parseState["errors"])
        stats["recenterrors"] = recenterrors
        return stats

def _succes(parseState, date, comments):
    parseState["lastHarvestDate"] = _reformatDate(date)
    parseState["errors"] = []
    match = NUMBERS_RE.match(comments)
    if match:
        parseState["harvested"], parseState["uploaded"], parseState["deleted"], parseState["total"] = match.groups()

def _error(parseState, date, comments):
    parseState["errors"].append((_reformatDate(date), comments))

def _reformatDate(aDate):
    return aDate[0:len('YYYY-MM-DD')] + 'T' + aDate[len('YYYY-MM-DD '):len('YYYY-MM-DD HH:MM:SS')] + 'Z'
        
