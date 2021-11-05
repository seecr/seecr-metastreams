from seecr.test import SeecrTestCase
from meresco.components import Bucket

from metastreams.users._actions import parse_arguments

class ActionsTest(SeecrTestCase):
    def testParseArguments(self):
        self.assertEqual({}, parse_arguments(b'', wanted=[]).__dict__)

    def testMultipleArguments(self):
        self.assertEqual({
            'delegate': ['efd4b964-5be1-4e42-a241-4f6721fa2758', 'b2c633ee-ddf7-4a2b-af70-04382577ca6a'],
            'identifier': '069235c5-d6ef-42b5-9719-647b806b5643',
            'targetType': 'composite'},
            parse_arguments(b'identifier=069235c5-d6ef-42b5-9719-647b806b5643&domainId=prod10&targetType=composite&name=Composite+Test&delegate=efd4b964-5be1-4e42-a241-4f6721fa2758&delegate=b2c633ee-ddf7-4a2b-af70-04382577ca6a', wanted=['identifier', 'delegate', 'targetType']).__dict__)

    def testWildcardArguments(self):
        self.assertEqual(
            {'a': '10', 'extra_a': '1', 'extra_b': '2', 'extra_c': '3'}, 
            parse_arguments(b'extra_a=1&extra_b=2&extra_c=3&a=10&b=20', wanted=['a', 'extra_*']).asDict())
