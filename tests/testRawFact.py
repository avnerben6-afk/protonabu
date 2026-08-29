""" Module: Protonabu Raw Fact Test Module
    - Author: Avner Ben
        - Created: 11-Mar-2026
        - Improved: 24-Aug-2026
            - Prepared for release
    - Generator: Antigravity (Gemini 3.1 Pro)
        - Generated: 11-Mar-2026
"""

from protonabu.testing import BaseTestCase, test
from protonabu.util.error import Error
# [Additional]
from protonabu.rawFact import RawFact
from protonabu.rawFactTestData import testData


class RawFactTest(BaseTestCase):
    """ Raw Fact Test Case
    """
    def __init__(self, testIndex: int):
        """ to INITIALIZE Raw Fact Test Case
            - Input: test Index
        """
        # [Msg]: to INITIALIZE Base Test Case
        super().__init__(testData, testIndex)
        self.indentHistory = None

    def setUp(self):
        """ to set-up Raw Fact test case
        """
        # [Msg]: to set-up test case
        super().setUp()
        # [Alt "2"]: to adjust test configuration dynamically 
        if self.testIndex == 2:
            base_input = 'INPUT [OPT; STATE]: EXPECTED "result" 32 [xxx "original" yyy; gvgvg \'77\' 7]'.replace('OPTION;', 'OPTION "okojihygtyhiplpinu uihuhgygyg ijihhuhugug okokokokokook oplplplpl";')
            # to set expected test input
            self.expected = base_input
        # [Alt "5"]: to set test indent history
        elif self.testIndex == 5:
            self.indentHistory = [0, 4, 8, 12, 16]
        # [Alt "6"]: to set bad rank indent history
        elif self.testIndex == 6:
            self.indentHistory = [0, 4, 7, 12, 16]

    def doRunTest(self) -> str:
        """ to perform Raw Fact test case
            - Output: result
        """
        # [Msg]: to INITIALIZE Raw Fact
        fact = RawFact()
        # [Guard]: to test composite fact serialization
        try:
            # [Alt "custom indent history"]: to parse composite fact with custom indent history
            if self.indentHistory is not None:
                fact.fromCompositeFact(self.testData[self.testIndex].testInput, self.indentHistory)
            # [Alt]: to parse composite fact with default indentation
            else:
                fact.fromCompositeFact(self.testData[self.testIndex].testInput)           
            testOutput = fact.toCompositeFact()
            # [Esc]: test Index of self equals rest
            if self.testIndex == 5:
                return testOutput[0].expandtabs(4)
            return testOutput[0]
        # [Esc Error]: "Error"
        except Error:
            # [Esc Done]: "6"
            if self.testIndex == 6:
                return 'Error'
            raise

    def processResult(self, actual: str) -> str:
        """ to process result of Raw Fact test case
            - Input: actual
            - Output: result
        """
        return actual

def main(isRefreshExpectedTestData: bool = False):
    """ to perform Raw Fact Test Cases
        - Input [Opt "False"]: is Refresh Expected Test Data
        - Output: "Result state"
        - Contains: Success indicator
        - Contains: number of test cases
    """
    # [Msg]: to perform Unit Test
    return test(
        RawFactTest,
        range(1, len(testData) + 1),
        isRefreshExpectedTestData
    )

# [Msg; Opt]: to perform Raw Fact Test Cases
if __name__ == '__main__':
    main()
