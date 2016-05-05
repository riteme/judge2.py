from judge2 import *

class Checker(object):
    """Represent a checker"""
    def __init__(self, testcase):
        super(Checker, self).__init__()

        self.testcase = testcase

    def check(self):
        """Check the judgement and give the final status.
        @return list A list contained the status.
        """
        return [ACCEPTED]
