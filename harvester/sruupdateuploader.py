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

from xml.sax.saxutils import escape as xmlEscape
from virtualuploader import VirtualUploader, UploaderException
from httplib import HTTPConnection

recordUpdate = """<?xml version="1.0" encoding="UTF-8"?>
<updateRequest xmlns:srw="http://www.loc.gov/zing/srw/" xmlns:ucp="http://www.loc.gov/ucp">
    <srw:version>1.0</srw:version>
    <ucp:action>info:srw/action/1/%(action)s</ucp:action>
    <ucp:recordIdentifier>%(recordIdentifier)s</ucp:recordIdentifier>
    <srw:record>
        <srw:recordPacking>%(recordPacking)s</srw:recordPacking>
        <srw:recordSchema>%(recordSchema)s</srw:recordSchema>
        <srw:recordData>%(recordData)s</srw:recordData>
    </srw:record>
</updateRequest>"""

class SruUpdateUploader(VirtualUploader):
    def __init__(self, sruUpdateTarget, eventlogger, collection="ignored"):
        VirtualUploader.__init__(self, eventlogger)
        self._target = sruUpdateTarget

    def send(self, anUpload):
        anId = anUpload.id
        self.logLine('UPLOAD.SEND', 'START', id = anId)

        recordData = '<document>%s</document>' % ''.join(
                ['<part name="%s">%s</part>' % (xmlEscape(partName), xmlEscape(partValue)) for partName, partValue in anUpload.parts.items()])

        action = "replace"
        recordIdentifier= xmlEscape(anId)
        recordPacking = 'xml'
        recordSchema = xmlEscape(partName)
        self._sendData(recordUpdate % locals())

        self.logLine('UPLOAD.SEND', 'END', id = anId)

    def delete(self, anUpload):
        self.logDelete(anUpload.id)
        action = "delete"
        recordIdentifier = xmlEscape(anUpload.id)
        recordPacking = 'xml'
        recordSchema = 'ignored'
        recordData = '<ignored/>'
        self._sendData(recordUpdate % locals())


    def info(self):
        return 'Uploader connected to: %s:%s%s'%(self._target.baseurl, self._target.port, self._target.path)


    def _sendData(self, data):
        connection = HTTPConnection(self._target.baseurl, self._target.port)
        connection.putrequest("POST", self._target.path)
        connection.putheader("Host", self._target.baseurl)
        connection.putheader("Content-Type", "text/xml; charset=\"utf-8\"")
        connection.putheader("Content-Length", str(len(data)))
        connection.endheaders()
        connection.send(data)

        result = connection.getresponse()
        message = result.read()
        if result.status != 200 or 'srw:diagnostic' in message:
            raise Exception(message)