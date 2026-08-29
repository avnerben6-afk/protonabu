""" Module: Protonabu Test Infrastructure
    - Author: Avner Ben
        - Created: 1-Jan-2025
        - Improved: 28-Aug-2026
            - Moved into Protonabu
"""

from dataclasses import dataclass
from typing import Any, Optional, Iterable
import unittest
import types
import sys
import os
from pathlib import Path

from ..util.stringUtil import IdCounter
from ..util.error import Error


@dataclass
class TestData:
    """ Test Data
    """
    title: str
    factName: str = ''
    testInput: Any = ''
    expectedOutput: str = ''


class BaseTestCase(unittest.TestCase):
    """ Base Test Case
        - Description: generic base class for data-driven test cases
    """
    def __init__(self, 
        # - Input: test data
        testData: dict[int, TestData] | int, 
        # - Input: test index
        testIndex: Optional[int] = None
    ):
        """ to initialize Base Test Case
            - Exported
            - Input: test Data
            - Input [Opt "None"]: test Index
        """
        super().__init__('runTest')
        # [Opt]: to get global test data by index
        if isinstance(testData, int) and testIndex is None:
            self.testIndex = testData
            self.testData = getattr(type(self), 'testData', {})
        # [Alt]: to use provided test data
        else:
            self.testData = testData if isinstance(testData, dict) else {}
            self.testIndex = testIndex if testIndex is not None else 0
        self.expected: str = ''
        self.actual: list[str] = []
    
    def shortDescription(self):
        """ to describe test case for display
            - Exported
            - Output: result
        """
        # [Esc]: global test data
        if self.testData and self.testIndex in self.testData:
            # to get description from test data
            return f'{self.testData[self.testIndex].title} [{self.testIndex}]'
        # to get hard-coded test-case descriptor
        return unittest.TestCase.shortDescription(self)

    def setUp(self):
        """ to set-up test case
            - Exported
        """
        # [Opt]: to get expected output from test data
        if self.testData and self.testIndex in self.testData:
            self.expected = self.testData[self.testIndex].expectedOutput

    def runTest(self):
        """ to perform Base Test Case
            - Exported
        """
        # [Msg]: to load test case
        self.load()
        # [Msg]: to evaluate test case result
        self.evaluate(self.doRunTest())

    def tearDown(self):
        """ to tear-down test case
            - Exported
        """
        # [Msg]: to reset all initialized ID Counters
        IdCounter.resetAll()

    def load(self):
        """ to load test case
            - Exported
        """
        pass

    def doRunTest(self) -> Any:
        """ to perform test case action
            - Exported
            - Output: result
        """
        pass

    def evaluate(self, actual: Any):
        """ to evaluate test result against expected output
            - Exported
            - Input: actual
        """
        # [Opt]: to process the result of test case
        if isinstance(actual, str):
            actual = self.processResult(actual)
        # [Msg]: to [Using; Using]: to assert equal
        self.assertEqual(actual, self.expected)

    def processResult(self, actual: str) -> str:
        """ to process the result of test case
            - Exported
            - Input: actual
            - Output: result
        """
        actual = actual.expandtabs().strip()
        # to strip test-result lines
        self.actual = [x.rstrip() for x in actual.split('\n')]
        return '\n'.join(self.actual)


class TestBatch:
    """ Test Batch
        - Intent: to group multiple test suites for batch execution
    """
    def __init__(self, *args):
        """ to INITIALIZE Test Batch
            - Exported
        """
        self.suites: list[tuple[type, list[int], bool, dict[int, TestData]]] = []
        # [Alt]: to parse single 3-tuple argument
        if len(args) == 3 and isinstance(args[0], type) and not isinstance(args[1], type):
            testType, testIds, isRefresh = args
            testIdsList = list(testIds) if testIds is not None else []
            testData = getattr(testType, 'testData', {})
            self.suites.append((testType, testIdsList, isRefresh, testData))
        # [Alt]: to parse tuple arguments
        else:
            # [Scan]: to parse tuple arguments
            for t in args:
                # [Opt]: to handle four test arguments
                if len(t) == 4:
                    self.suites.append(t)
                # [Alt]: to handle three test arguments
                elif len(t) == 3:
                    testType, testIds, isRefresh = t
                    testIdsList = list(testIds) if testIds is not None else []
                    testData = getattr(testType, 'testData', None)
                    # [Alt]: to get global test data
                    if testData is None and testIdsList:
                        # [Guard]: to get global test data by test-type
                        try:
                            testData = getattr(testType(testIdsList[0]), 'testData', {})
                        # [Esc]: Exception
                        except Exception:
                            testData = {}
                    # [Alt]: to reset test data
                    elif testData is None:
                        testData = {}
                    self.suites.append((testType, testIdsList, isRefresh, testData))


def test(
    testTypeOrBatch: Any, 
    testIds: Optional[Iterable[int]] = None, 
    isRefreshExpectedTestData: bool = False
) -> tuple[bool, int]:
    """ to perform Unit Test
        - Exported
        - Intent: generalizes the standard test module main function
        - Input: test Type Or Batch
        - Input [Opt "None"]: test Ids
        - Input [Opt "False"]: is Refresh Expected Test Data
        - Output: result
    """
    # [Alt]: to use provided test batch
    if isinstance(testTypeOrBatch, TestBatch):
        batch = testTypeOrBatch
    # [Alt]: to INITIALIZE test batch
    else:
        batch = TestBatch(testTypeOrBatch, testIds, isRefreshExpectedTestData)
    totalErrors, allSuccessful = 0, True
    # [Scan]: to perform test suite
    for testType, ids, isRefresh, testData in batch.suites:
        testCases = (testType(tp) for tp in ids)
        suite = unittest.TestSuite(testCases)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        allSuccessful &= result.wasSuccessful()
        totalErrors += len(result.errors) + len(result.failures)
    return allSuccessful, totalErrors


def getTestModules(
    globalsDict: Optional[dict[str, Any]] = None,
    argv: Optional[list[str]] = None
) -> tuple[list[types.ModuleType], bool]:
    """ to obtain the list of test modules to run
        - Exported
        - Input [State]: command line arguments.
        - Input [Opt "None"]: argv
        - Output: result
    """
    # [Alt]: to get testing arguments from the command line
    if argv is None:
        argv = sys.argv[1:]
    # [Alt]: to use provided testing arguments
    else:
        argv = list(argv)
    
    # [Opt]: to decide globals Dict
    if globalsDict is None:
        import inspect
        frame = inspect.currentframe().f_back
        globalsDict = frame.f_globals if frame else {}

    isRefreshExpectedTestData = False
    # [Opt]: to refresh testing argument
    if '--refresh' in argv:
        refresh_idx = argv.index('--refresh')
        # [Opt]: to parse refresh test flag value
        if refresh_idx + 1 < len(argv):
            isRefreshExpectedTestData = argv[refresh_idx + 1].upper() == 'Y'
            argv.pop(refresh_idx + 1)
        # to forget refresh testing argument
        argv.pop(refresh_idx)

    is_default = not argv or (len(argv) == 1 and "_ALL_" in argv)
    # [Esc Error]: "Cannot specify both _ ALL_ and test modules"
    if "_ALL_" in argv and len(argv) > 1:
        raise ValueError("Cannot specify both _ALL_ and test modules")
    
    module_names_to_run = [] if is_default else argv
    test_modules = []
    
    # [Scan]: to add test module
    for name, obj in globalsDict.items():
        # [Esc Once]: not a module
        if not isinstance(obj, types.ModuleType): continue
        # [Alt "default"]: to consider adding test module by default
        if is_default:
            if name.startswith("test"):
                test_modules.append(obj)
        # [Alt]: to add explicitly requested test module 
        elif name in module_names_to_run:
            test_modules.append(obj)

    # [Scan]: to ensure requested test-module found
    for name in module_names_to_run:
        # [Esc]: name not in globals Dict
        if name not in globalsDict:
            raise Error(f"Test module not found", [('Module', name)])
    return test_modules, isRefreshExpectedTestData


def runTestModules(test_modules: Iterable[Any], isRefreshExpectedTestData: bool = False) -> tuple[bool, int]:
    """ to run the test modules
        - Exported
        - Input: list of test modules to run
        - Input: refresh-expected-test-data indication
        - Output: result
    """
    path = Path().resolve()
    totalErrors: int = 0
    failedModules: list[str] = []
    modulesList = list(test_modules)
    
    # [Scan; Opt "has main"]: to process test module
    for testModule in modulesList:
        os.chdir(path)
        if hasattr(testModule, 'main'):
            # [Guard]: to run test module
            try:
                result = testModule.main(isRefreshExpectedTestData)
                isSuccessful, numErrors = result if isinstance(result, tuple) else (result if isinstance(result, bool) else True, 0)
                # [Opt]: to record test failure
                if not isSuccessful:
                    failedModules.append(testModule.__name__.split(".")[-1])
                    totalErrors += numErrors
            # [Esc Error]: "TypeError"
            except TypeError:
                # [Guard]: to run test module without arguments
                try: 
                    result = testModule.main()
                    isSuccessful, numErrors = result if isinstance(result, tuple) else (result if isinstance(result, bool) else True, 0)
                    # [Opt]: to record test failure
                    if not isSuccessful:
                        failedModules.append(testModule.__name__.split(".")[-1])
                        totalErrors += numErrors
                except Exception as e:
                    print(f"Error running {testModule.__name__}: {e}")
                    failedModules.append(testModule.__name__.split(".")[-1])
    print()
    # [Scan]: to print test failure message
    for failure in failedModules:
        print(failure, "failed")
    # [Msg]: to print test summary message
    print(f"Ran {len(modulesList)} test suites: failures={len(failedModules)}, errors={totalErrors}")
    return len(failedModules) == 0, totalErrors
