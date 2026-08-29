""" Module: Standard Snippet Adapter Test Module
    - Author: Avner Ben
        - Created: 17-May-2026
        - Improved: 24-Aug-2026
            - Prepared for release
    - Generator: Antigravity (Gemini 3.1 Pro)
        - Generated: 17-May-2026
"""

import json
import xml.etree.ElementTree as ET

from protonabu.testing import TestData, BaseTestCase, test
# [Additional]
from protonabu.factSnippet import (
    ProtonabuSnippet,
    ProtonabuMemorySource,
    ProtonabuSnippetInMemory,
)
# [Additional]
from protonabu.adapter.adapterFactory import snippetAdapterFactory
# [Additional]
from protonabu.adapter.std.MarkdownSnippetAdapter.markdownSnippetAdapter import (
    MarkdownSnippetAdapter, MarkdownAdapterSource
)
# [Additional]
from protonabu.adapter.std.JsonSnippetAdapter.jsonSnippetAdapter import (
    JsonSnippetAdapter, JsonAdapterSource
)
# [Additional]
from protonabu.adapter.std.XmlSnippetAdapter.xmlSnippetAdapter import (
    XmlSnippetAdapter, XmlAdapterSource
)

NABU_LINES = [
    'PROJECT: Test Project',
    '    PRODUCT: Widget Factory',
    '        PART: Engine',
    '            CAPABILITY: to start engine',
    '                REQUIRES: to check fuel level',
    '                    USING: "fuel gauge"',
    '                REQUIRES: to ignite',
    '        USE CASE: to operate widget',
    '            REQUIRES: to start engine',
]
MARKDOWN_LINES = [
    '- PROJECT: Test Project',
    '    - PRODUCT: Widget Factory',
    '        - PART: Engine',
    '            - CAPABILITY: to start engine',
    '                - REQUIRES: to check fuel level',
    '                    - USING: "fuel gauge"',
    '                - REQUIRES: to ignite',
    '        - USE CASE: to operate widget',
    '            - REQUIRES: to start engine',
]
NABU_TEXT = '\n'.join(NABU_LINES)
MARKDOWN_TEXT = '\n'.join(MARKDOWN_LINES)

testData = {
    1: TestData(
        title='Factory registration',
        expectedOutput='OK'
    ),
    2: TestData(
        title='Markdown input adaptation',
        testInput=MARKDOWN_LINES,
        expectedOutput=NABU_TEXT
    ),
    3: TestData(
        title='Markdown output adaptation',
        testInput=NABU_LINES,
        expectedOutput=MARKDOWN_TEXT
    ),
    4: TestData(
        title='Markdown full snippet round-trip',
        testInput=MARKDOWN_LINES,
        expectedOutput='9'
    ),
    5: TestData(
        title='JSON round-trip',
        testInput=NABU_LINES,
        expectedOutput='9'
    ),
    6: TestData(
        title='XML round-trip',
        testInput=NABU_LINES,
        expectedOutput='9'
    ),
}


class SnippetAdapterTestCase(BaseTestCase):
    """ Snippet Adapter Test Case
    """
    def __init__(self, testIndex: int):
        """ to INITIALIZE Snippet Adapter Test Case
            - Input: test Index
        """
        # [Msg]: to initialize Base Test Case
        super().__init__(testData, testIndex)

    def doRunTest(self) -> str:
        """ to perform Snippet Adapter test case
            - Output: result
        """
        # [Esc]: test Index of self equals rest
        if self.testIndex == 1:
            return self._testFactoryRegistration()
        # [Esc]: test Index of self equals rest
        if self.testIndex == 2:
            return self._testMarkdownInputAdaptation()
        # [Esc]: test Index of self equals rest
        if self.testIndex == 3:
            return self._testMarkdownOutputAdaptation()
        # [Esc]: test Index of self equals rest
        if self.testIndex == 4:
            return self._testMarkdownFullSnippet()
        # [Esc]: test Index of self equals rest
        if self.testIndex == 5:
            return self._testJsonRoundTrip()
        # [Esc]: test Index of self equals rest
        if self.testIndex == 6:
            return self._testXmlRoundTrip()
        return 'Unknown test'

    def _testFactoryRegistration(self) -> str:
        """ to test Snippet Adapter factory registration
            - Output: result
        """
        assert snippetAdapterFactory.hasAdapter('design.md'), '.md not registered'
        assert snippetAdapterFactory.hasAdapter('data.json'), '.json not registered'
        assert snippetAdapterFactory.hasAdapter('schema.xml'), '.xml not registered'
        assert not snippetAdapterFactory.hasAdapter('project.nabu'), '.nabu should not be registered'
        assert not snippetAdapterFactory.hasAdapter('code.py'), '.py should not be registered'
        assert isinstance(snippetAdapterFactory.getAdapter('design.md'), MarkdownSnippetAdapter)
        assert isinstance(snippetAdapterFactory.getAdapter('data.json'), JsonSnippetAdapter)
        assert isinstance(snippetAdapterFactory.getAdapter('schema.xml'), XmlSnippetAdapter)
        return 'OK'

    def _testMarkdownInputAdaptation(self) -> str:
        """ to test Markdown input line adaptation
            - Output: result
        """
        # [Msg]: to INITIALIZE Line Adapter Fact Stream
        # - Using: to INITIALIZE Protonabu Snippet source In Memory
        source = MarkdownAdapterSource(ProtonabuMemorySource(self.testData[self.testIndex].testInput))
        return '\n'.join(list(source))

    def _testMarkdownOutputAdaptation(self) -> str:
        """ to test Markdown output line adaptation
            - Output: result
        """
        # [Msg]: to INITIALIZE Protonabu Snippet source In Memory
        outSource = ProtonabuMemorySource()
        # [Msg]: to INITIALIZE Line Adapter Fact Stream
        adapter = MarkdownAdapterSource(outSource)
        # [Scan]: to add Nabu lines to Line Adapter Fact Stream
        for line in self.testData[self.testIndex].testInput:
            adapter.add(line)
        return '\n'.join(list(outSource.source))

    def _testMarkdownFullSnippet(self) -> str:
        """ to test full Markdown snippet iteration
            - Output: result
        """
        # [Msg]: to INITIALIZE Markdown Snippet Adapter
        adapter = MarkdownSnippetAdapter()
        # [Msg]: to INITIALIZE Protonabu Snippet source In Memory
        rawSnippet = ProtonabuSnippetInMemory(self.testData[self.testIndex].testInput, 'test.md')
        # [Msg]: to import facts thru Snippet Adapter
        adapted = adapter.adaptInput(rawSnippet)
        # [Msg]: to get raw facts from adapted snippet
        rawFacts = list(adapted)
        return str(len(rawFacts))

    def _testJsonRoundTrip(self) -> str:
        """ to test JSON round-trip
            - Output: result
        """
        # [Msg]: to parse original Nabu lines into RawFacts
        origSnippet = ProtonabuSnippetInMemory(self.testData[self.testIndex].testInput, 'test.nabu')
        origFacts = list(origSnippet)
        # [Msg]: to build JSON tree from flat list of ranked Raw Facts
        jsonTree = JsonAdapterSource._buildTree(origFacts)
        # [Msg]: to convert JSON tree to JSON text
        jsonText = json.dumps(jsonTree, indent=2, ensure_ascii=False)
        # [Msg]: to INITIALIZE Protonabu Snippet source In Memory
        jsonSource = ProtonabuMemorySource(jsonText.split('\n'))
        # [Msg]: to INITIALIZE Line Adapter Fact Stream
        adapterSource = JsonAdapterSource(jsonSource, isInput=True)
        # [Msg]: to INITIALIZE Protonabu Snippet
        reconSnippet = ProtonabuSnippet(adapterSource, 'test.json')
        # [Msg]: to get raw facts from adapted snippet
        reconFacts = list(reconSnippet)
        # to verify JSON snippet fact count
        assert len(origFacts) == len(reconFacts), f'Count mismatch: {len(origFacts)} vs {len(reconFacts)}'
        # [Scan]: to verify JSON labels and arguments
        for i, (orig, recon) in enumerate(zip(origFacts, reconFacts)):
            assert orig.label == recon.label, f'Label mismatch at {i}: {orig.label!r} vs {recon.label!r}'
            assert orig.arg == recon.arg, f'Arg mismatch at {i}: {orig.arg!r} vs {recon.arg!r}'
        return str(len(reconFacts))

    def _testXmlRoundTrip(self) -> str:
        """ to test XML round-trip
            - Output: result
        """
        # [Msg]: to create Protonabu Snippet In Memory
        origSnippet = ProtonabuSnippetInMemory(self.testData[self.testIndex].testInput, 'test.nabu')
        origFacts = list(origSnippet)
        # [Msg]: to build XML tree from flat list of ranked Raw Facts
        rootElem = XmlAdapterSource._buildTree(origFacts)
        # [Msg]: to add indentation to XML element tree for pretty printing
        XmlAdapterSource._indent(rootElem)
        # [Msg]: to convert XML tree to XML text
        xmlText = ET.tostring(rootElem, encoding='unicode')
        # [Msg]: to INITIALIZE Protonabu Snippet source In Memory
        xmlSource = ProtonabuMemorySource(xmlText.split('\n'))
        # [Msg]: to INITIALIZE Line Adapter Fact Stream
        adapterSource = XmlAdapterSource(xmlSource, isInput=True)
        # [Msg]: to INITIALIZE Protonabu Snippet
        reconSnippet = ProtonabuSnippet(adapterSource, 'test.xml')
        # [Msg]: to get raw facts from adapted snippet
        reconFacts = list(reconSnippet)
        # to verify XML snippet fact count
        assert len(origFacts) == len(reconFacts), f'Count mismatch: {len(origFacts)} vs {len(reconFacts)}'
        # [Scan]: to verify XML labels and arguments
        for i, (orig, recon) in enumerate(zip(origFacts, reconFacts)):
            assert orig.label == recon.label, f'Label mismatch at {i}: {orig.label!r} vs {recon.label!r}'
            assert orig.arg == recon.arg, f'Arg mismatch at {i}: {orig.arg!r} vs {recon.arg!r}'
        return str(len(reconFacts))

    def processResult(self, actual: str) -> str:
        """ to process the result of Snippet Adapter test case
            - Input: actual
            - Output: result
        """
        return actual.strip()


def main(isRefreshExpectedTestData: bool = False) -> tuple[bool, int]:
    """ to perform Snippet Adapter Test Cases
        - Input: refresh expected test-data flag
        - Output: "Result state"
        - Contains: Success indicator
        - Contains: number of test cases
    """
    # [Msg]: to perform Unit Test
    return test(
        SnippetAdapterTestCase,
        range(1, len(testData) + 1),
        isRefreshExpectedTestData
    )

# [Opt]: to perform Snippet Adapter Test Cases
if __name__ == '__main__':
    main()
