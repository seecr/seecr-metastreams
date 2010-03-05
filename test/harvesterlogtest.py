## begin license ##
#
#    "Meresco Harvester" consists of two subsystems, namely an OAI-harvester and
#    a web-control panel.
#    "Meresco Harvester" is originally called "Sahara" and was developed for
#    SURFnet by:
#        Seek You Too B.V. (CQ2) http://www.cq2.nl
#    Copyright (C) 2006-2007 SURFnet B.V. http://www.surfnet.nl
#    Copyright (C) 2007-2008 SURF Foundation. http://www.surf.nl
#    Copyright (C) 2007-2010 Seek You Too (CQ2) http://www.cq2.nl
#    Copyright (C) 2007-2009 Stichting Kennisnet Ict op school.
#       http://www.kennisnetictopschool.nl
#    Copyright (C) 2009 Tilburg University http://www.uvt.nl
#    Copyright (C) 2010 Stichting Kennisnet http://www.kennisnet.nl
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

import unittest,os, time
from merescoharvester.harvester.harvesterlog import HarvesterLog
from merescoharvester.harvester import harvesterlog
from merescoharvester.harvester.eventlogger import LOGLINE_RE
from tempfile import mkdtemp
from shutil import rmtree


class HarvesterLogTest(unittest.TestCase):
    def setUp(self):
        self.stateDir = mkdtemp()
        self.logDir = mkdtemp()

    def tearDown(self):
        rmtree(self.stateDir)
        rmtree(self.logDir)

    def testSameDate(self):
        logger = HarvesterLog(stateDir=self.stateDir, logDir=self.logDir,name='someuni')
        date=logger.printTime()[:10]
        self.assertTrue(logger.isCurrentDay(date))
        self.assertFalse(logger.isCurrentDay('2005-01-02'))

    def testHasWork(self):
        logger = HarvesterLog(stateDir=self.stateDir, logDir=self.logDir,name='someuni')
        self.assertEqual((None,None,0),(logger.from_,logger.token,logger.total))
        self.assert_(logger.hasWork())
        logger.from_=time.strftime('%Y-%m-%d')
        self.assert_(not logger.hasWork())
        logger.token='SomeToken'
        self.assert_(logger.hasWork())
        logger.from_='2005-01-02'
        self.assert_(logger.hasWork())
        logger.token=None
        self.assert_(logger.hasWork())

    def testHasWorkBeforeAndAfterDoingWork(self):
        logger = HarvesterLog(stateDir=self.stateDir, logDir=self.logDir,name= 'name')
        self.assertTrue(logger.hasWork())
        logger.startRepository('RepositoryName')
        logger.begin()
        logger.updateStatsfile(0,0,0,0)
        logger.done()
        logger.endRepository(None)
        logger.close()
        logger = HarvesterLog(stateDir=self.stateDir, logDir=self.logDir,name= 'name')
        self.assertFalse(logger.hasWork())


    def createMockMailer(self, name):
        self.mockMailerName=name
        self.mockMailer=MockMailer()
        return self.mockMailer

    def testLoggingAlwaysStartsNewline(self):
        "Tests an old situation that when a log was interrupted, it continued on the same line"
        f = open(self.stateDir+'/name.stats','w')
        f.write('Started: 2005-01-02 16:12:56, Harvested/Uploaded/Total: 199/200/1650, Don"crack"')
        f.close()
        logger = HarvesterLog(stateDir=self.stateDir, logDir=self.logDir,name= 'name')
        logger.startRepository('RepositoryName')
        logger.close()
        lines = open(self.stateDir+'/name.stats').readlines()
        self.assertEqual(2,len(lines))

    def testLogLine(self):
        logger = HarvesterLog(stateDir=self.stateDir, logDir=self.logDir,name= 'name')
        logger.begin()
        logger.updateStatsfile(1, 2, 3)
        logger.done()
        logger.endRepository(None)
        logger.close()
        lines = open(self.stateDir+'/name.stats').readlines()
        eventline = open(self.logDir+'/name.events').readlines()[0].strip()
        #Total is now counted based upon the id's
        self.assertEqual(', Harvested/Uploaded/Deleted/Total: 1/2/3/0, Done:',lines[0][:50])
        date,event,id,comments = LOGLINE_RE.match(eventline).groups()
        self.assertEquals('SUCCES', event.strip())
        self.assertEquals('name', id)
        self.assertEquals('Harvested/Uploaded/Deleted/Total: 1/2/3/0, ResumptionToken: None',comments)

    def testLogLineError(self):
        logger = HarvesterLog(stateDir=self.stateDir, logDir=self.logDir,name= 'name')
        logger.begin()
        try:
            logger.updateStatsfile(1, 2, 3)
            raise Exception('FATAL')
        except:
            logger.endWithException()
        logger.close()
        lines = open(self.stateDir+'/name.stats').readlines()
        eventline = open(self.logDir+'/name.events').readlines()[0].strip()
        #Total is now counted based upon the id's
        self.assertEqual(', Harvested/Uploaded/Deleted/Total: 1/2/3/0 busy..., Error: ',lines[0][:60])
        date,event,id,comments = LOGLINE_RE.match(eventline).groups()
        self.assertEquals('ERROR', event.strip())
        self.assertEquals('name', id)
        self.assert_(comments.startswith('Traceback (most recent call last):|File "'))
        self.assert_('harvesterlogtest.py", line ' in comments)
        self.assert_(comments.endswith(', in testLogLineError raise Exception(\'FATAL\')|Exception: FATAL'))

    def testLogWithoutDoubleIDs(self):
        f = open(self.stateDir+'/name.ids','w')
        f.writelines(['id:1\n','id:2\n','id:1\n'])
        f.close()
        logger = HarvesterLog(stateDir=self.stateDir, logDir=self.logDir,name= 'name')
        self.assertEquals(2,logger.totalids())
        logger.logID('id:3')
        self.assertEquals(3,logger.totalids())
        logger.logID('id:3')
        logger.logID('id:2')
        self.assertEquals(3,logger.totalids())

    def testLogDeleted(self):
        logger = HarvesterLog(stateDir=self.stateDir, logDir=self.logDir,name='emptyrepoi')
        self.assertEquals(None,logger.from_)
        self.assertEquals(0, logger.total)
        self.assertEquals(None, logger.token)
        f = open(self.stateDir+'/name.stats','w')
        f.write('Started: 2005-01-02 16:12:56, Harvested/Uploaded/Total: 199/200/1650, Done: 2005-04-22 11:48:30, ResumptionToken: resumption')
        f.close()
        logger = HarvesterLog(stateDir=self.stateDir, logDir=self.logDir,name='name')
        self.assertEquals('2005-01-02',logger.from_)
        self.assertEquals(1650, logger.total)
        self.assertEquals('resumption', logger.token)
        f = open(self.stateDir+'/name.stats','w')
        f.write('Started: 2005-01-02 16:12:56, Harvested/Uploaded/Total: 199/200/1650, Done: 2005-04-22 11:48:30, ResumptionToken: resumption\n')
        f.write('Started: 2005-01-02 16:12:56, Harvested/Uploaded/Deleted/Total: 0/0/0/0, Done: Deleted all id\'s\n')
        f.close()
        logger = HarvesterLog(stateDir=self.stateDir, logDir=self.logDir,name='name')
        self.assertEquals(None, logger.token)
        self.assertEquals(None,logger.from_)
        self.assertEquals(0, logger.total)

    def testMarkDeleted(self):
        f = open(self.stateDir+'/name.stats','w')
        f.write('Started: 2005-01-02 16:12:56, Harvested/Uploaded/Total: 199/200/1650, Done: 2005-04-22 11:48:30, ResumptionToken: resumption')
        f.close()
        logger = HarvesterLog(stateDir=self.stateDir, logDir=self.logDir,name='name')
        self.assertEquals('resumption', logger.token)
        logger.markDeleted()
        logger.close()
        logger = HarvesterLog(stateDir=self.stateDir, logDir=self.logDir,name='name')
        self.assertEquals(None, logger.token)
        self.assertEquals(None,logger.from_)
        self.assertEquals(0, logger.total)


class MockMailer(object):
    def send(self, message):
        self.message=message

