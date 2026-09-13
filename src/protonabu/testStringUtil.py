""" Module: Protonabu String Utilities Test Suite
    - Author: Avner Ben
        - Created: 28-Aug-2026
    - Generator: Antigravity (Gemini 3.7 Flash)
        - Generated: 28-Aug-2026
"""

import unittest
from hypothesis import given, strategies as st
from .testing import BaseTestCase, TestData, test
from .util.stringUtil import (
    IdCounter,
    NameMaker,
    nameMaker,
    QuantityNarrator,
    quantityNarrator,
    narrateQuantity,
    cleanEnd,
    unquote,
    unbracket,
    quoteIf,
    toCamel,
    unCamel,
    sanitizeProgrammaticName,
    makeBilingualName,
    concatModifiers,
    pluralize,
    parseDocDate,
    restoreDocDate,
)

testData = {
    1: TestData(
        title="Standard NameMaker conversion and abbreviation",
        testInput="to update the current version Number",
        expectedOutput="updateCurrentVersionNum"
    ),
    2: TestData(
        title="Trailing article and preposition stripping",
        testInput=["to update the", "to stage files at", "run with"],
        expectedOutput="update | stageFiles | run"
    ),
    3: TestData(
        title="Namespace-aware uniqueness in scope",
        testInput=("to update", "scope1"),
        expectedOutput="update | update1 | update2"
    ),
    4: TestData(
        title="Uniqueness registry clearing",
        testInput="to update",
        expectedOutput="update"
    ),
    5: TestData(
        title="Unmake programmatic name to literate form",
        testInput="updateCurrentVersionNum",
        expectedOutput="update Current Version Number"
    ),
    6: TestData(
        title="Magic/dunder method translation with custom setMagicMethods",
        testInput=["__init__", "__del__", "custom_action_method"],
        expectedOutput="INITIALIZE | FINALIZE | custom action method"
    ),
    7: TestData(
        title="QuantityNarrator singular, plural, and zero narration",
        testInput=[("module", 0), ("part", 13), ("use case", 6), ("product capability", 1), ("part capability", 52)],
        expectedOutput="No modules, 13 parts, 6 use cases, one product capability, 52 part capabilities"
    ),
    8: TestData(
        title="QuantityNarrator edge cases and alternative call signatures",
        testInput=[("capability", 10), ("key", 5), ("process", 3)],
        expectedOutput="10 capabilities, 5 keys, 3 processes"
    ),
    9: TestData(
        title="Quote, unquote, bracket, and unbracket",
        testInput=["hello world", "'already quoted'", "[nested]", "clean...;;;"],
        expectedOutput='"hello world" | already quoted | nested | clean'
    ),
    10: TestData(
        title="Camel case transformations (toCamel / unCamel)",
        testInput=["hello_world_variable", "HelloWorldVariable"],
        expectedOutput="HelloWorldVariable | Hello World Variable"
    ),
    11: TestData(
        title="sanitizeProgrammaticName dot-chain to ownership and punctuation stripping",
        testInput="self.userProfile.settings.theme == 'dark'",
        expectedOutput="theme of settings of user Profile of self equals dark"
    ),
    12: TestData(
        title="Pluralize regular and irregular nouns",
        testInput=["child", "criterion", "datum", "personnel", "box", "city", "key"],
        expectedOutput="children | criteria | data | personnel | boxes | cities | keys"
    ),
    13: TestData(
        title="DocDate parse and restore round-trip",
        testInput="28-Aug-2026",
        expectedOutput="28-Aug-2026"
    ),
    14: TestData(
        title="IdCounter sequence generation and resetAll",
        testInput=None,
        expectedOutput="group_1, group_2 | reset -> group_1"
    ),
    15: TestData(
        title="makeBilingualName and concatModifiers",
        testInput=None,
        expectedOutput="Name (Hebrew) | Opt; State"
    ),
    16: TestData(
        title="NameMaker suggestSimilar candidate retrieval",
        testInput="PropertyMngr",
        expectedOutput="['PropertyManager']"
    ),
}


class StringUtilTestCase(BaseTestCase):
    """ to test Protonabu string utilities
    """
    def __init__(self, testId: int):
        """ to INITIALIZE String Util test case
        """
        super().__init__(testData, testId)

    def doRunTest(self):
        """ to perform String Util test case
        """
        datum = self.testData[self.testIndex]
        inp = datum.testInput

        if self.testIndex == 1:
            return nameMaker.makeProgrammaticName(inp, capFirst=False)

        elif self.testIndex == 2:
            r1 = nameMaker.makeProgrammaticName(inp[0], capFirst=False)
            r2 = nameMaker.makeProgrammaticName(inp[1], capFirst=False)
            r3 = nameMaker.makeProgrammaticName(inp[2], capFirst=False)
            return f"{r1} | {r2} | {r3}"

        elif self.testIndex == 3:
            nameMaker.clearRegistries()
            scope = inp[1]
            n1 = nameMaker.makeUniqueProgrammaticName(inp[0], scopes=[scope], capFirst=False)
            n2 = nameMaker.makeUniqueProgrammaticName(inp[0], scopes=[scope], capFirst=False)
            n3 = nameMaker.makeUniqueProgrammaticName(inp[0], scopes=[scope], capFirst=False)
            return f"{n1} | {n2} | {n3}"

        elif self.testIndex == 4:
            scope = "scope_clear"
            nameMaker.clearRegistries()
            n1 = nameMaker.makeUniqueProgrammaticName(inp, scopes=[scope], capFirst=False)
            nameMaker.clearRegistries()
            n2 = nameMaker.makeUniqueProgrammaticName(inp, scopes=[scope], capFirst=False)
            return n2

        elif self.testIndex == 5:
            return nameMaker.unMakeProgrammaticName(inp)

        elif self.testIndex == 6:
            NameMaker.setMagicMethods({'__init__': 'INITIALIZE', '__del__': 'FINALIZE'})
            r1 = nameMaker.translateMagicMethod(inp[0])
            r2 = nameMaker.translateMagicMethod(inp[1])
            r3 = nameMaker.translateMagicMethod(inp[2])
            return f"{r1} | {r2} | {r3}"

        elif self.testIndex == 7:
            return QuantityNarrator(inp).narrate()

        elif self.testIndex == 8:
            res1 = QuantityNarrator(inp).narrate()
            res2 = quantityNarrator.narrate(inp)
            res3 = narrateQuantity(inp)
            assert res1 == res2 == res3
            return res1

        elif self.testIndex == 9:
            q = quoteIf(inp[0])
            uq = unquote(inp[1])
            ub = unbracket(inp[2])
            ce = cleanEnd(inp[3])
            return f"{q} | {uq} | {ub} | {ce}"

        elif self.testIndex == 10:
            tc = toCamel(inp[0])
            uc = unCamel(inp[1])
            return f"{tc} | {uc}"

        elif self.testIndex == 11:
            return sanitizeProgrammaticName(inp)

        elif self.testIndex == 12:
            plurals = [pluralize(w) for w in inp]
            return " | ".join(plurals)

        elif self.testIndex == 13:
            ts = parseDocDate(inp)
            restored = restoreDocDate(ts)
            return restored

        elif self.testIndex == 14:
            c = IdCounter(prefix='group')
            id1 = c.next()
            id2 = c.next()
            IdCounter.resetAll()
            id3 = c.next()
            return f"{id1}, {id2} | reset -> {id3}"

        elif self.testIndex == 15:
            bi = makeBilingualName("Name", "Hebrew")
            mods = concatModifiers(["Opt", "", "State"])
            return f"{bi} | {mods}"

        elif self.testIndex == 16:
            nameMaker.clearRegistries()
            nameMaker.register("PropertyManager", ["ScopeA"])
            nameMaker.register("ProjectManager", ["ScopeA"])
            nameMaker.register("Accountant", ["ScopeA"])
            suggestions = nameMaker.suggestSimilar("PropertyMngr", scope="ScopeA")
            return str(suggestions)

        return "Unknown test index"


class StringUtilPropertyTestCase(unittest.TestCase):
    """ Property-based tests for string utilities using Hypothesis
    """
    @given(st.lists(st.text(alphabet=st.characters(min_codepoint=65, max_codepoint=90), min_size=2, max_size=8), min_size=2, max_size=15))
    def test_name_maker_uniqueness_guarantee(self, raw_names):
        nameMaker.clearRegistries()
        generated = []
        for n in raw_names:
            unique = nameMaker.makeUniqueProgrammaticName(f"Entity{n}", scopes=["testScope"])
            generated.append(unique)
        self.assertEqual(len(generated), len(set(generated)))

    @given(st.sampled_from(['to', 'the', 'a', 'an', 'of', 'at', 'by', 'in', 'on', 'with', 'for', 'from']))
    def test_trailing_preposition_stripping(self, prep):
        result = nameMaker.makeProgrammaticName(f"update data {prep}", capFirst=False)
        self.assertEqual(result, "updateData")
    @given(st.text(alphabet=st.characters(blacklist_characters='"\'[]', blacklist_categories=('Cs', 'Cc', 'Z'))).filter(lambda s: len(s) > 0))
    def test_unquote_quote_roundtrip(self, s):
        quoted = f'"{s}"'
        self.assertEqual(unquote(quoted), s)

    @given(st.text(alphabet=st.characters(blacklist_characters='"\'[]', blacklist_categories=('Cs', 'Cc', 'Z'))).filter(lambda s: len(s) > 0))
    def test_unbracket_bracket_roundtrip(self, s):
        bracketed = f'[{s}]'
        self.assertEqual(unbracket(bracketed), s)


def main(isRefreshExpectedTestData: bool = False) -> tuple[bool, int]:
    """ to perform String Util test suite
    """
    ok_data, errors_data = test(StringUtilTestCase, testData.keys(), isRefreshExpectedTestData)
    prop_suite = unittest.TestLoader().loadTestsFromTestCase(StringUtilPropertyTestCase)
    prop_res = unittest.TextTestRunner(verbosity=2).run(prop_suite)
    all_ok = ok_data and prop_res.wasSuccessful()
    total_errors = errors_data + len(prop_res.errors) + len(prop_res.failures)
    return all_ok, total_errors


if __name__ == '__main__':
    main()
