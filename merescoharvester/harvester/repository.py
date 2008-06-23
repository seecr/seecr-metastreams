## begin license ##
#
#    "Meresco Harvester" consists of two subsystems, namely an OAI-harvester and
#    a web-control panel.
#    "Meresco Harvester" is originally called "Sahara" and was developed for 
#    SURFnet by:
#        Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2006-2007 SURFnet B.V. http://www.surfnet.nl
#    Copyright (C) 2007-2008 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2008 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
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

from cq2utils import binderytools
from mapping import Mapping
from harvesterlog import HarvesterLog
from harvester import Harvester, HARVESTED, NOTHING_TO_DO
from deleteids import DeleteIds, readIds, writeIds
from saharaobject import SaharaObject
import os.path, shutil
from eventlogger import NilEventLogger
from virtualuploader import UploaderFactory
from cq2utils.timeslot import Timeslot
import time

nillogger = NilEventLogger()
DONE = 'Done.'

class RepositoryException(Exception):
    pass

class Action:
    def __init__(self, repository, stateDir, logDir):
        self._repository = repository
        self._stateDir = stateDir
        self._logDir = logDir
    def do(self):
        """
        perform action and return
        (if the action is finished/done, a Message about what happened.)
        """
        raise NotImplementedError
    def info(self):
        return  str(self.__class__).split('.')[-1]

class NoneAction(Action):
    def do(self):
        return False, ''
    def info(self):
        return ''

class HarvestAction(Action):
    def _createHarvester(self):
        return Harvester(self._repository, self._stateDir, self._logDir)
    
    def do(self):
        if self._repository.shopClosed():
            return False, 'Not harvesting outside timeslots.'
         
        harvester = self._createHarvester()
        return False, harvester.harvest()

class DeleteIdsAction(Action):
    def do(self):
        d = DeleteIds(self._repository, self._stateDir, self._logDir)
        d.delete()
        return True, 'Deleted'

class SmoothAction(Action):
    def __init__(self, repository, stateDir, logDir):
        Action.__init__(self, repository, stateDir, logDir)
        self.filename = os.path.join(self._stateDir, self._repository.key + '.ids')
        self.oldfilename = self.filename + ".old"

    def do(self):
        if self._repository.shopClosed():
            return False, 'Not smoothharvesting outside timeslots.'

        if not os.path.isfile(self.oldfilename):
            result = self._smoothinit()
        else:
            result = self._harvest()
        if result == NOTHING_TO_DO:
            result = self._finish()
        return result == DONE, 'Smooth reharvest: ' + result

    def _smoothinit(self):
        if os.path.isfile(self.filename):
            shutil.move(self.filename, self.oldfilename)
        else:
            open(self.oldfilename, 'w').close()
        open(self.filename, 'w').close()
        logger = HarvesterLog(self._stateDir, self._logDir, self._repository.key)
        try:
            logger.markDeleted()
        finally:
            logger.close()
        return     'initialized.'

    def _finish(self):
        deletefilename = self.filename + '.delete'
        writeIds(deletefilename, readIds(self.oldfilename) - readIds(self.filename))
        self._delete(deletefilename)
        os.remove(self.oldfilename)
        return DONE

    def _delete(self, filename):
        d = DeleteIds(self._repository, self._stateDir, self._logDir)
        d.deleteFile(filename)

    def _harvest(self):
        harvester = Harvester(self._repository, self._stateDir, self._logDir)
        return harvester.harvest()

class ActionFactoryException(Exception):
    pass

class ActionFactory:
    def createAction(self, repository, stateDir, logDir):
        if repository.action == 'clear':
            return DeleteIdsAction(repository, stateDir=stateDir, logDir=logDir)
        if repository.action == 'refresh':
            return SmoothAction(repository, stateDir=stateDir, logDir=logDir)
        if repository.use == 'true' and repository.action == '':
            return HarvestAction(repository, stateDir=stateDir, logDir=logDir)
        if repository.use == "" and repository.action == '':
            return NoneAction(repository, stateDir=stateDir, logDir=logDir)
        raise ActionFactoryException("Action '%s' not supported."%repository.action)

class Repository(SaharaObject):
    def __init__(self, domainId, repositoryId):
        SaharaObject.__init__(self, ['repositoryGroupId', 'baseurl', 'set',
            'collection', 'metadataPrefix', 'use',  'targetId', 'mappingId', 'action'], ['shopclosed'])
        self.domainId = domainId
        self.id = repositoryId
        self.mockUploader = None
        self.uploadfulltext = True
        self._copyOldStuff()

    def _copyOldStuff(self):
        #aan de bezoeker: gelieve een van deze regels code weg te halen. (KvS, JJ)
        self.key = self.id
        self.url = self.baseurl
        self.institutionkey = self.repositoryGroupId

    def closedSlots(self):
        if not hasattr(self, '_closedslots'):
            if self.shopclosed:
                self._closedslots = map(lambda txt: Timeslot(txt), self.shopclosed)
            else:
                self._closedslots = []
        return self._closedslots

    def shopClosed(self, dateTuple = time.localtime()[:5]):
        return reduce(lambda lhs, rhs: lhs or rhs, map(lambda x:x.areWeWithinTimeslot( dateTuple), self.closedSlots()), False)

    def target(self):
        return self._saharaget.getTarget(self.domainId, self.targetId)

    def mapping(self):
        return self._saharaget.getMapping(self.domainId, self.mappingId)

    def createUploader(self, logger):
        if self.mockUploader:
            return self.mockUploader
        return UploaderFactory().createUploader(self.target(), logger, self.collection)

    def _createAction(self, stateDir, logDir):
        return ActionFactory().createAction(self, stateDir=stateDir, logDir=logDir)

    def do(self, stateDir, logDir, eventlogger=nillogger):
        if not (stateDir or logDir):
            raise RepositoryException('Missing stateDir and/or logDir')
        action = self._createAction(stateDir=stateDir, logDir=logDir)
        if action.info():
            eventlogger.logLine('START',action.info(), id=self.key)
        actionIsDone, message = action.do()
        if  actionIsDone:
            self.action = ''
            self._saharaget.repositoryActionDone(self.domainId, self.id)
        if message:
            eventlogger.logLine('END', message, id = self.key)
        return message