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
# (c) 2005, Seek You Too B.V.
#
# $Id: startharvester.py 4825 2007-04-16 13:36:24Z TJ $
#
from harvesterlog import HarvesterLog
from eventlogger import EventLogger, NilEventLogger
from harvester import Harvester
from sseuploader import LoggingUploader
import sys, os, optparse
from saharaget import SaharaGet
from time import sleep
import traceback
from timedprocess import TimedProcess


class StartHarvester:
    def __init__(self):
        if len(sys.argv[1:]) == 0:
                        sys.argv.append('-h')
        self.parser = optparse.OptionParser()
        args = self.parse_args()
        self.__dict__.update(args.__dict__)
        
        if not self.domainId:
            self.parser.error("Specify domain")
        
        self.saharaget = SaharaGet(self.saharaurl, self.setActionDone)
        
        self.repository = self.repositoryId and self.saharaget.getRepository(self.domainId, self.repositoryId)
        
        if not self.repository:
            self.restartWithLoop(self.domainId)
        
        if self.forceTarget:
            self.repository.targetId = self.forceTarget
        if self.forceMapping:
            self.repository.mappingId = self.forceMapping
        
        self.full_logpath = os.path.join(self.logpath, self.domainId)
        
        os.path.isdir(self.full_logpath) or os.makedirs(self.full_logpath)
        self.eventlogger = EventLogger(os.path.join(self.full_logpath, 'harvester.log'))
    
        if self.uploadLog:
            self.repository.mockUploader = LoggingUploader(EventLogger(self.uploadLog))
        
    def parse_args(self):
        self.parser.add_option("-d", "--domain", dest="domainId",
                        help="Mandatory argument denoting the domain.", metavar="DOMAIN")
        self.parser.add_option("-s", "--saharaurl", dest="saharaurl",
                        help="The url of the SAHARA web interface, e.g. https://username:password@sahara.example.org", default="http://localhost")
        self.parser.add_option("-r", "--repository", dest="repositoryId",
                        help="Process a single repository within the given domain. Defaults to all repositories from the domain.", metavar="REPOSITORY")
        self.parser.add_option("-l", "--logpath", dest="logpath",
                        help="Set the logpath, if not use <current directory>/log", metavar="DIRECTORY", default=self.getDefaultLogpath())
        self.parser.add_option("--uploadLog", "", dest="uploadLog",
                        help="Set the mockUploadLogFile to which the fields are logged instead of uploading to a server.", metavar="FILE")
        self.parser.add_option("--force-target", "", dest="forceTarget",
                        help="Overrides the repository's target", metavar="TARGETID")
        self.parser.add_option("--force-mapping", "", dest="forceMapping",
                        help="Overrides the repository's mapping", metavar="MAPPINGID")
        self.parser.add_option("--no-action-done", "", action="store_false", dest="setActionDone", default=True, help="Do not set SAHARA's actions", metavar="TARGETID")
        (options, args) = self.parser.parse_args()
        return options
    
    def getDefaultLogpath(self):
        return os.path.join(os.getcwd(), 'log')
    
    def restartWithLoop(self, domainId):
        for key in self.saharaget.getRepositoryIds(domainId):
            args = sys.argv[:1] + ['--repository='+key] + sys.argv[1:]
            t = TimedProcess()
            try:
                one_hour = 60 * 60
                TIMEOUT = one_hour
                SIG_INT = 2
                t.executeScript(args, TIMEOUT, SIG_INT)
            except KeyboardInterrupt, e:     
                t.terminate()
                raise
        sys.exit()
    
    def start(self):
        try:
            self.repository.do(self.full_logpath, self.eventlogger)
        except:
            xtype,xval,xtb=sys.exc_info()
            self.eventlogger.error('|'.join(map(str.strip, traceback.format_exception(xtype,xval,xtb))), id=self.repository.id)
        sleep(1)

if __name__ == '__main__':
    startharvester = StartHarvester()
    startharvester.start()
