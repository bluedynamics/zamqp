# Copyright 2009, BlueDynamics Alliance - http://bluedynamics.com
# GNU General Public License Version 2 or later

import unittest
import doctest 
from pprint import pprint
from interlude import interact

optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE

TESTFILES = [
    '_api.txt',
]

class LocalEvent(object):
    """test event implementation.
    """
    def __init__(self, name):
        self.name = name

def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(
            file, 
            optionflags=optionflags,
            globs={'interact': interact,
                   'pprint': pprint},
        ) for file in TESTFILES
    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite') 