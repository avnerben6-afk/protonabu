""" Module: XML Snippet Adapter Module
    - Author: Avner Ben
        - Created: 17-May-2026
    - Generator: Antigravity (Claude Opus 4.6)
        - Generated: 17-May-2026
"""

import xml.etree.ElementTree as ET
from typing import Iterator

from ....util.error import Error
# [Additional]
from ....rawFact import RawFact, EditDirective
# [Additional]
from ....factSnippet import ProtonabuSnippet
# [Additional]
from ...snippetAdapter import FactSnippetAdapter


class XmlAdapterSource(ProtonabuSnippet.ISource):
    """ XML Fact Stream
        - Purpose: to adapt Protonabu Fact Snippet source for XML format
        - Description: On input, parses XML and yields reconstructed
          Nabu fact lines. On output, collects Nabu fact lines and
          serializes them as XML on close.
    """

    def __init__(self, wrapped: ProtonabuSnippet.ISource, isInput: bool = True):
        """ to INITIALIZE XML Fact Stream
            - Input: wrapped
            - Input [Opt "True"]: is Input
        """
        # Contains [1:1 By Reference]: Fact Stream
        self.wrapped: ProtonabuSnippet.ISource = wrapped
        self.isInput: bool = isInput
        self.outputLines: list[str] = []

    # -- XML ↔ RawFact conversion utilities --

    @staticmethod
    def _elementToFact(elem: ET.Element, rank: int) -> RawFact:
        """ to convert XML element to Raw Fact
            - Input: elem
            - Input: rank
            - Output: result
            - definitive [Part]
        """
        # [Msg]: to INITIALIZE Raw Fact
        fact = RawFact()
        fact.label = elem.tag.upper().replace('_', ' ')
        # [Opt]: to set converted XML label modifiers
        if 'modifier' in elem.attrib:
            fact.labelModifiers = [
                m.strip() for m in elem.attrib['modifier'].split(';')
            ]
        # [Opt]: to set converted XML argument
        if 'argument' in elem.attrib:
            fact.arg = elem.attrib['argument']
        # [Opt]: to set converted XML argument modifiers
        if 'argModifier' in elem.attrib:
            fact.argModifiers = [
                m.strip() for m in elem.attrib['argModifier'].split(';')
            ]
        # [Opt]: to set converted XML comment
        if 'comment' in elem.attrib:
            fact.comment = elem.attrib['comment']
        # [Opt]: to set converted XML edit directive
        if 'editDirective' in elem.attrib:
            fact.editDirective = EditDirective.fromSymbol(elem.attrib['editDirective'])
        fact.rank = rank
        return fact

    @staticmethod
    def _factToElement(fact: RawFact) -> ET.Element:
        """ to convert Raw Fact to XML element
            - Input: fact
            - Output: result
        """
        # [Msg]: to convert label to XML tag
        tag = fact.label.lower().replace(' ', '_')
        attribs = {}
        # [Opt]: to convert label modifiers to XML attributes
        if fact.labelModifiers:
            attribs['modifier'] = '; '.join(fact.labelModifiers)
        # [Opt]: to convert argument to XML attribute
        if fact.arg:
            attribs['argument'] = fact.arg
        # [Opt]: to convert argument modifiers to XML attributes
        if fact.argModifiers:
            attribs['argModifier'] = '; '.join(fact.argModifiers)
        # [Opt]: to convert comment to XML attribute
        if fact.comment:
            attribs['comment'] = fact.comment
        # [Opt]: to convert edit directive to XML attribute
        if fact.editDirective:
            attribs['editDirective'] = fact.editDirective.toSymbol()
        return ET.Element(tag, attribs)

    @staticmethod
    def _flattenXml(elem: ET.Element, rank: int = 1) -> list[RawFact]:
        """ to flatten XML tree to list of Raw Facts
            - Input: elem
            - Input [Opt "1"]: rank
            - Output: result
        """
        # [Msg]: to convert XML element to Raw Fact
        facts = [XmlAdapterSource._elementToFact(elem, rank)]
        # [Scan]: to flatten children recursively
        for child in elem:
            facts.extend(XmlAdapterSource._flattenXml(child, rank + 1))
        return facts

    # -- ISource implementation --

    def add(self, fact: str):
        """ to append line to <XML> Fact Stream
            - Input: fact
        """
        self.outputLines.append(fact)

    def __iter__(self) -> Iterator[str]:
        """ to TRAVERSE <XML> Fact Stream
            - Output: result
        """
        # to collect all XML text from wrapped source
        text = '\n'.join(line.rstrip('\n').rstrip('\r') for line in self.wrapped)
        # [Guard]: to parse XML from string
        try:
            root = ET.fromstring(text)
        except ET.ParseError as e:
            raise Error('Invalid XML in snippet', [('Error', str(e))])
        # [Alt]: to collect nabu root XML elements
        if root.tag.lower() == 'nabu':
            elements = list(root)
        # [Alt]: to collect single XML element
        else:
            elements = [root]
        # [
        #     Scan "elements"; 
        #     Scan "to flatten XML tree to list of Raw Facts"; 
        #     Scan "to restore Labeled Fact to one or more Fact lines"
        # ]: 
        # [Scan]: to for elem in elements
        for elem in elements:
            # [Scan; Scan]: to handle fact (xml Snippet Adapter at 0133)
            for fact in self._flattenXml(elem):
                for line in fact.toCompositeFact():
                    yield line

    def close(self):
        """ to close <XML> Fact Stream
        """
        # [Opt]: to reconstruct XML fact hierarchy from collected output lines
        if self.outputLines:
            facts = []
            # [Scan "outputLines"]: to reconstruct facts from collected output lines
            for line in self.outputLines:
                # [Esc Once]: "blank line"
                if not line.strip(): continue
                # [Msg]: to INITIALIZE Raw Fact
                fact = RawFact()
                # [Msg]: to parse one Labeled Fact raw elements from Fact stream
                fact.fromCompositeFact(line)
                # [Opt]: to pick labeled fact for XML output
                if fact.label:
                    facts.append(fact)
            # [Msg]: to build XML tree from flat facts
            rootElem = self._buildTree(facts)
            # [Msg]: to build XML tree from flat list of ranked Raw Facts
            xmlText = ET.tostring(rootElem, encoding='unicode')
            # [Msg]: to add indentation to XML element tree for pretty printing
            self._indent(rootElem)
            # [Msg]: to convert XML DOM to string
            xmlText = ET.tostring(rootElem, encoding='unicode', xml_declaration=True)
            # [Scan "XML text lines"]: to write XML to wrapped source
            for line in xmlText.split('\n'):
                self.wrapped.add(line)
        # [Msg]: to close fact stream
        self.wrapped.close()

    @staticmethod
    def _buildTree(facts: list[RawFact]) -> ET.Element:
        """ to build XML tree from flat list of ranked Raw Facts
            - Input: facts
            - Output: result
        """
        # [Msg]: to initialize XML root
        root = ET.Element('nabu')
        # [Esc]: "empty fact list"
        if not facts: return root
        stack: list[tuple[int, ET.Element]] = [(0, root)]
        # [Scan "facts"]: to build XML tree from anked Raw Facts
        for fact in facts:
            # [Msg]: to convert Raw Fact to XML element
            elem = XmlAdapterSource._factToElement(fact)
            # [Rpt]: to pop expired XML stack frame
            while stack and stack[-1][0] >= fact.rank:
                # [Msg]: to pop list
                stack.pop()
            # [Alt]: to insert XML node under parent
            if stack:
                stack[-1][1].append(elem)
            # [Alt]: to insert XML node under root
            else:
                root.append(elem)
                stack = [(0, root)]
            # [Msg]: to push frame to the XML stack
            stack.append((fact.rank, elem))
        return root

    @staticmethod
    def _indent(elem: ET.Element, level: int = 0):
        """ to add indentation to XML element tree for pretty printing
            - Input: elem
            - Input [Opt "0"]: level
        """
        # to set base XML indentation
        indent = '\n' + '  ' * level
        # [Alt]: to indent XML element lines
        if len(elem):
            # [Opt]: to indent XML element text
            if not elem.text or not elem.text.strip():
                elem.text = indent + '  '
            # [Opt]: to indent XML element tail
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent
            # [Scan]: to add indentation to XML element tree for pretty printing
            for child in elem:
                XmlAdapterSource._indent(child, level + 1)
            # [Opt]: to indent last child XML element
            if not child.tail or not child.tail.strip():
                child.tail = indent
        # [Alt]: to indent XML leaf element
        elif level and (not elem.tail or not elem.tail.strip()):
            elem.tail = indent


class XmlSnippetAdapter(FactSnippetAdapter):
    """ XML Snippet Adapter
        - Purpose: to adapt Protonabu Fact Snippet for XML format
        - Description: Converts between standard Nabu fact syntax and
        XML element format by wrapping the snippet source
        in an XmlAdapterSource.
    """
    fileExtensions = ['.xml']

    def adaptInput(self, snippet: ProtonabuSnippet) -> ProtonabuSnippet:
        """ to import facts thru <XML> Snippet Adapter
            - Exported: Xml
            - Input: XML snippet
            - Output: Native format snippet
            - definitive [Part]
        """
        # [Msg]: to INITIALIZE Protonabu Snippet
        # - Using: to INITIALIZE Snippet Adapter Source
        #   - Using: snippet source
        adapted = ProtonabuSnippet(
            XmlAdapterSource(snippet.source, isInput=True),
            snippet.fileName,
            snippet.isImporting
        )
        return adapted

    def adaptOutput(self, snippet: ProtonabuSnippet) -> ProtonabuSnippet:
        """ to export facts thru <XML> Snippet Adapter
            - Exported: Xml
            - Input: Native format snippet
            - Output: XML format snippet
        """
        # [Msg]: to INITIALIZE Protonabu Snippet
        # - Using: to INITIALIZE Snippet Adapter Source
        #   - Using: snippet source
        adapted = ProtonabuSnippet(
            XmlAdapterSource(snippet.source, isInput=False),
            snippet.fileName,
            snippet.isImporting
        )
        return adapted
