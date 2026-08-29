""" Module: Protonabu Loop Utilities Test Suite
    - Author: Avner Ben
        - Created: 28-Aug-2026
    - Generator: Antigravity (Gemini 3.7 Flash)
        - Generated: 28-Aug-2026
"""

from protonabu.testing import BaseTestCase, TestData, test
from protonabu.util.loops import (
    first,
    find,
    findBehind,
    findIndex,
    findNested,
    exists,
    count,
    findNoCase,
    firstValid,
    iterUp,
    iterUps,
)

testData = {
    1: TestData(
        title="first on non-empty and empty iterables",
        testInput=None,
        expectedOutput="[10, 20]->10, []->None"
    ),
    2: TestData(
        title="find and findIndex",
        testInput=None,
        expectedOutput="find(>25)=30, findIndex(>25)=2, findIndex(>100)=-1"
    ),
    3: TestData(
        title="findBehind with transform function",
        testInput=None,
        expectedOutput="matched='HELLO_WORLD'"
    ),
    4: TestData(
        title="findNested across child collections",
        testInput=None,
        expectedOutput="found=42"
    ),
    5: TestData(
        title="exists, count, and findNoCase",
        testInput=None,
        expectedOutput="exists=True, count=4, findNoCase='Banana'"
    ),
    6: TestData(
        title="firstValid fallback logic",
        testInput=None,
        expectedOutput="case1='first', case2='second', case3=''"
    ),
    7: TestData(
        title="iterUp linear single-parent hierarchy",
        testInput=None,
        expectedOutput="Middle -> Root"
    ),
    8: TestData(
        title="iterUp cycle protection (Node A -> Node B -> Node A)",
        testInput=None,
        expectedOutput="NodeA -> NodeB"
    ),
    9: TestData(
        title="iterUps DAG / diamond hierarchy without duplication",
        testInput=None,
        expectedOutput="LeftParent -> TopRoot -> RightParent"
    ),
    10: TestData(
        title="iterUps cyclic network protection",
        testInput=None,
        expectedOutput="NetA -> NetB -> NetC"
    ),
    11: TestData(
        title="iterUp on root node with no parent",
        testInput=None,
        expectedOutput="none"
    ),
}


class LoopUtilitiesTestCase(BaseTestCase):
    """ to test Protonabu loop utilities
    """
    def __init__(self, testId: int):
        """ to INITIALIZE Loop Utilities test case
        """
        super().__init__(testData, testId)

    def doRunTest(self):
        """ to perform Loop Utilities test case
        """
        if self.testIndex == 1:
            r1 = first([10, 20, 30])
            r2 = first([])
            return f"[10, 20]->{r1}, []->{r2}"

        elif self.testIndex == 2:
            nums = [10, 20, 30, 40]
            f = find(nums, lambda x: x > 25)
            idx1 = findIndex(nums, lambda x: x > 25)
            idx2 = findIndex(nums, lambda x: x > 100)
            return f"find(>25)={f}, findIndex(>25)={idx1}, findIndex(>100)={idx2}"

        elif self.testIndex == 3:
            items = ['abc', 'hello_world', 'xyz']
            # Return transformed uppercase of word containing 'hello'
            res = findBehind(items, lambda x: x.upper() if 'hello' in x else None)
            return f"matched='{res}'"

        elif self.testIndex == 4:
            class Parent:
                def __init__(self, children):
                    self.children = children

            parents = [Parent([1, 2, 3]), Parent([10, 20]), Parent([42, 99])]
            found = findNested(parents, lambda p: p.children, lambda c: c == 42)
            return f"found={found}"

        elif self.testIndex == 5:
            fruits = ['Apple', 'Banana', 'Orange', 'Avocado', 'Berry']
            ex = exists(fruits, lambda f: f.startswith('O'))
            cnt = count(fruits, lambda f: f.startswith('A') or f.startswith('B'))
            fnc = findNoCase(fruits, 'bAnAnA')
            return f"exists={ex}, count={cnt}, findNoCase='{fnc}'"

        elif self.testIndex == 6:
            c1 = firstValid('first', 'second')
            c2 = firstValid('', 'second')
            c3 = firstValid('', '')
            return f"case1='{c1}', case2='{c2}', case3='{c3}'"

        elif self.testIndex == 7:
            # Linear hierarchy: Leaf -> Middle -> Root -> None
            parents = {
                'Leaf': 'Middle',
                'Middle': 'Root',
                'Root': None
            }
            chain = list(iterUp('Leaf', lambda n: parents.get(n)))
            return ' -> '.join(chain)

        elif self.testIndex == 8:
            # Cyclic hierarchy: NodeA -> NodeB -> NodeA
            cycle = {
                'Start': 'NodeA',
                'NodeA': 'NodeB',
                'NodeB': 'NodeA'
            }
            chain = list(iterUp('Start', lambda n: cycle.get(n)))
            return ' -> '.join(chain)

        elif self.testIndex == 9:
            # Diamond DAG:
            #      TopRoot
            #      /     \
            # LeftParent RightParent
            #      \     /
            #       Child
            graph = {
                'Child': ['LeftParent', 'RightParent'],
                'LeftParent': ['TopRoot'],
                'RightParent': ['TopRoot'],
                'TopRoot': []
            }
            chain = list(iterUps('Child', lambda n: graph.get(n, [])))
            return ' -> '.join(chain)

        elif self.testIndex == 10:
            # Cyclic network graph:
            # Start -> NetA <-> NetB -> NetC -> NetA
            net_graph = {
                'Start': ['NetA'],
                'NetA': ['NetB'],
                'NetB': ['NetA', 'NetC'],
                'NetC': ['NetA']
            }
            chain = list(iterUps('Start', lambda n: net_graph.get(n, [])))
            return ' -> '.join(chain)

        elif self.testIndex == 11:
            chain = list(iterUp('StandaloneRoot', lambda n: None))
            return ' -> '.join(chain) if chain else 'none'

        return "Unknown test index"


def main(isRefreshExpectedTestData: bool = False) -> tuple[bool, int]:
    """ to perform Protonabu loop utilities test suite
    """
    return test(LoopUtilitiesTestCase, testData.keys(), isRefreshExpectedTestData)


if __name__ == '__main__':
    main()
