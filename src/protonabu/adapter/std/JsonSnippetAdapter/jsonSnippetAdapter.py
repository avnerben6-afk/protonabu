""" Module: JSON Snippet Adapter
    - Author: Avner Ben
        - Created: 17-May-2026
    - Generator: Antigravity (Claude Opus 4.6)
        - Generated: 17-May-2026
"""

import json
from typing import Iterator

from ....util.error import Error
# [Additional]
from ....rawFact import RawFact, EditDirective
# [Additional]
from ....factSnippet import ProtonabuSnippet
# [Additional]
from ...snippetAdapter import FactSnippetAdapter


class JsonAdapterSource(ProtonabuSnippet.ISource):
    """ JSON Fact Stream
        - Purpose: to adapt Fact Stream for JSON format
        - Description: On input, parses JSON and yields reconstructed
          Nabu fact lines. On output, collects Nabu fact lines and
          serializes them as JSON on close.
    """

    def __init__(self, wrapped: ProtonabuSnippet.ISource, isInput: bool = True):
        """ to INITIALIZE JSON Fact Stream
            - Input: wrapped
            - Input [Opt "True"]: is Input
        """
        # Contains [1:1 By Reference]: Fact Stream
        self.wrapped: ProtonabuSnippet.ISource = wrapped
        self.isInput: bool = isInput
        self.outputLines: list[str] = []

    # -- JSON ↔ RawFact conversion utilities --

    @staticmethod
    def _factToDict(fact: RawFact) -> dict:
        """ to convert Raw Fact to JSON-serializable dictionary
            - Input: Raw Fact
            - Output: JSON-serializable dictionary
            - definitive [Part]
        """
        # to prepare JSON fact label
        result = {'label': fact.label}
        # [Opt]: to add label modifiers to JSON fact
        if fact.labelModifiers:
            result['labelModifiers'] = fact.labelModifiers
        # [Opt]: to add argument to JSON fact
        if fact.arg:
            result['argument'] = fact.arg
        # [Opt]: to add argument modifiers to JSON fact
        if fact.argModifiers:
            result['argModifiers'] = fact.argModifiers
        # [Opt]: to add comment to JSON fact
        if fact.comment:
            result['comment'] = fact.comment
        # [Opt]: to add edit directive to JSON fact
        if fact.editDirective:
            result['editDirective'] = fact.editDirective.toSymbol()
        return result

    @staticmethod
    def _dictToFact(d: dict, rank: int) -> RawFact:
        """ to convert JSON fact dictionary to Raw Fact
            - Input: JSON fact dictionary
            - Output: Raw Fact
            - Input: rank
        """
        # [Msg]: to initialize Raw Fact from JSON fact dictionary
        fact = RawFact(
            label=d.get('label', ''),
            labelModifiers=d.get('labelModifiers'),
            arg=d.get('argument'),
            argModifiers=d.get('argModifiers')
        )
        # [Opt]: to convert persistence symbol to enum value
        if 'editDirective' in d:
            fact.editDirective = EditDirective.fromSymbol(d['editDirective'])
        # [Opt]: to convert JSON comment to string
        if 'comment' in d:
            fact.comment = d['comment']
        fact.rank = rank
        return fact

    @staticmethod
    def _flattenJson(node: dict, rank: int = 1) -> list[RawFact]:
        """ to flatten JSON tree to list of Raw Facts
            - Input: JSON fact dictionary
            - Output: List of Raw Facts
            - Input [Opt "1"]: rank
        """
        facts = []
        # [Msg]: to convert JSON fact dictionary to Raw Fact
        fact = JsonAdapterSource._dictToFact(node, rank)
        facts.append(fact)
        # [Msg; Scan]: to flatten JSON tree to list of Raw Facts
        for child in node.get('children', []):
            facts.extend(JsonAdapterSource._flattenJson(child, rank + 1))
        return facts

    # -- ISource implementation --

    def add(self, fact: str):
        """ to append line to <JSON> Fact Stream
            - Input: fact
        """
        self.outputLines.append(fact)

    def __iter__(self) -> Iterator[str]:
        """ to TRAVERSE <JSON> Fact Stream
            - Output: result
        """
        # to collect all JSON text from wrapped source
        text = '\n'.join(line.rstrip('\n').rstrip('\r') for line in self.wrapped)
        # [Guard]: to parse JSON from string
        try:
            data = json.loads(text)
        # [Esc Error]: "Invalid JSON in snippet"
        except json.JSONDecodeError as e:
            raise Error('Invalid JSON in snippet', [('Error', str(e))])
        # [Opt]: to normalize to list of root facts
        if isinstance(data, dict):
            data = [data]
        # [Scan]: to flatten JSON tree to list of Raw Facts
        for root in data:
            # [Scan; Scan]: to handle fact (json Snippet Adapter at 0129)
            for fact in self._flattenJson(root):
                for line in fact.toCompositeFact():
                    yield line

    def close(self):
        """ to close <JSON> Fact Stream
        """
        # [Opt]: to reconstruct fact hierarchy from collected output lines
        if self.outputLines:
            facts = []
            # [Scan "output lines"]: to prepare JSON fact lines for printout
            for line in self.outputLines:
                # [Esc Once]: blank line
                if not line.strip(): continue
                # [Msg]: to INITIALIZE Raw Fact
                fact = RawFact()
                # [Msg]: to parse one Labeled Fact raw elements from Fact stream
                fact.fromCompositeFact(line)
                # [Opt]: to pick labeled fact for JSON output
                if fact.label:
                    facts.append(fact)
            # [Msg]: to build JSON tree from flat list of ranked Raw Facts
            root = self._buildTree(facts)
            # [Msg]: to serialize JSON tree to string
            jsonText = json.dumps(root, indent=2, ensure_ascii=False)
            # [Scan "jsonText"]: to write JSON line to wrapped source
            for line in jsonText.split('\n'):
                self.wrapped.add(line)
        # [Msg]: to close Fact Stream
        self.wrapped.close()

    @staticmethod
    def _buildTree(facts: list[RawFact]) -> list[dict]:
        """ to build JSON tree from flat list of ranked Raw Facts
            - Input: list of ranked Raw Facts
            - Output: JSON tree
        """
        # [Esc Done]: empty facts list
        if not facts: return []
        result = []
        stack: list[tuple[int, dict]] = []
        # [Scan "facts"]: to build JSON tree from flat list of ranked Raw Facts
        for fact in facts:
            # [Msg]: to convert Raw Fact to JSON-serializable dictionary
            node = JsonAdapterSource._factToDict(fact)
            # [Rpt]: to pop expired frame from the JSON stack
            while stack and stack[-1][0] >= fact.rank:
                # [Msg]: to pop list
                stack.pop()
            # [Alt]: to insert JSON fact root node
            if not stack:
                result.append(node)
            # [Alt]: to insert as child of parent frame
            else:
                parent = stack[-1][1]
                # [Opt]: to create children list in JSON parent fact
                if 'children' not in parent:
                    parent['children'] = []
                parent['children'].append(node)
            # [Msg]: to push fact frame to the JSON stack
            stack.append((fact.rank, node))
        return result


class JsonSnippetAdapter(FactSnippetAdapter):
    """ JSON Snippet Adapter
        - Purpose: to adapt Protonabu Fact Snippet for JSON format
        - Description: Converts between standard Nabu fact syntax and
        JSON tree format by wrapping the snippet source
        in a JsonAdapterSource.
    """
    fileExtensions = ['.json']

    def adaptInput(self, snippet: ProtonabuSnippet) -> ProtonabuSnippet:
        """ to import facts thru <JSON> Snippet Adapter
            - Exported: Json
            - Input: JSON snippet
            - Output: Native format snippet
            - definitive [Part]
        """
        # [Msg]: to INITIALIZE Protonabu Snippet
        # - Using: to INITIALIZE Snippet Adapter Source
        #   - Using: snippet source
        adapted = ProtonabuSnippet(
            JsonAdapterSource(snippet.source, isInput=True),
            snippet.fileName,
            snippet.isImporting
        )
        return adapted

    def adaptOutput(self, snippet: ProtonabuSnippet) -> ProtonabuSnippet:
        """ to export facts thru <JSON> Snippet Adapter
            - Exported: Json
            - Input: Native format snippet
            - Output: JSON format snippet
        """
        # [Msg]: to INITIALIZE Protonabu Snippet
        # - Using: to INITIALIZE Snippet Adapter Source
        #   - Using: snippet source
        adapted = ProtonabuSnippet(
            JsonAdapterSource(snippet.source, isInput=False),
            snippet.fileName,
            snippet.isImporting
        )
        return adapted
