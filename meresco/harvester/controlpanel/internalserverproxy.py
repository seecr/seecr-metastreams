## begin license ##
#
# "Meresco Harvester" consists of two subsystems, namely an OAI-harvester and
# a web-control panel.
# "Meresco Harvester" is originally called "Sahara" and was developed for
# SURFnet by:
# Seek You Too B.V. (CQ2) http://www.cq2.nl
#
# Copyright (C) 2015 Seecr (Seek You Too B.V.) http://seecr.nl
#
# This file is part of "Meresco Harvester"
#
# "Meresco Harvester" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Meresco Harvester" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Meresco Harvester"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from meresco.components.json import JsonDict, JsonList
from urllib import urlencode

class InternalServerProxy(object):
    def __init__(self, req):
        self._geturl = '%s/get?' % req.get_options()['internalServer']
        self._url = req._psp_url

    def getRepositoryGroup(self, identifier, domainId):
        return self.urlJsonDict(verb='GetRepositoryGroup', identifier=identifier, domainId=domainId)['response']['GetRepositoryGroup']

    def getRepository(self, identifier, domainId):
        return self.urlJsonDict(verb='GetRepository', identifier=identifier, domainId=domainId)['response']['GetRepository']

    def getTarget(self, identifier):
        return self.urlJsonDict(verb='GetTarget', identifier=identifier)['response']['GetTarget']

    def getMapping(self, identifier):
        return self.urlJsonDict(verb='GetMapping', identifier=identifier)['response']['GetMapping']

    def getDomain(self, identifier):
        return self.urlJsonDict(verb='GetDomain', identifier=identifier)['response']['GetDomain']

    def getDomainIds(self):
        return self.urlJsonDict(verb='GetDomainIds')['response']['GetDomainIds']

    def urlJsonDict(self, **kwargs):
        return JsonDict.load(self._url(self._geturl + urlencode(kwargs)))

    def urlJsonList(self, **kwargs):
        return JsonList.load(self._url(self._geturl + urlencode(kwargs)))