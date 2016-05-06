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
        try:
            standard = ""
            with open(self.testcase.standard_output) as f:
                standard = f.read()

            user = ""
            with open(self.testcase.user_output) as f:
                user = f.read()

            if standard == user:
                self.testcase.message = "All right"
                return [ACCEPTED]
            else:
                self.testcase.message = "Totally WRONG!"
                return [WRONG_ANSWER]

        except Exception as e:
            self.testcase.message = str(e)
            return [INTERNAL_ERROR]
