""" Module: Protonabu Schema Module
    - Author: Avner Ben
        - Created: 24-Jun-2026
            - Separated from fact Snippet Parser and revised
        - Improved: 24-Aug-2026
          - Prepared for release
    - Generator: Antigravity (Gemini 3.7 Flash)
        - Improved: 24-Aug-2026
"""

import sys
from types import ModuleType
from collections import defaultdict
from contextlib import suppress
from typing import Iterator, Optional, Callable, TextIO, Protocol, Sequence

from .util.error import Error, FactFileError
from .util.loops import first
# [Additional]
from .rawFact import RawFact, ProtonabuParsingStack
# [Additional]
from . import primitiveTokens, tokenizedFact
# [Additional]
from .factSnippet import ProtonabuSnippet, ProtonabuSnippetFromFile


class ITokenizer(Protocol):
    """ Tokenizer Interface
        - Purpose: Structural contract for Protonabu tokenizers (PyParsing or user-defined)
    """
    def parseString(self, s: str, parseAll: bool = True) -> Sequence[str]:
        """ to parse string into tokens
            - Exported
            - Input: string to parse
            - Input [Opt "True"]: parse all characters
            - Output: sequence of token strings
            - definitive [Part]
        """
        ...


class SchemaParsingStack(ProtonabuParsingStack["Label"]):
    """ Schema Parsing Stack
        - Purpose: to track nested Protonabu Schema
    """
    def __init__(self):
        """ to INITIALIZE Schema Parsing Stack
        """
        # [Msg]:to INITIALIZE Schema Parsing Stack
        # - Populates [ranks]: Label
        super().__init__()

    def endBlock(self, rank, label: str):
        """ to match explicit <Schema> Parsing Stack block ending with or without label
            - Input: rank
            - Input: label
            - definitive [Part]
        """
        # [Esc Error]: label mismatch
        if self.ranks[rank + 1][1].name != label.upper():
            raise Error('Block not opened above', [('Block', label.upper())])
        # [Msg]: to match explicit block ending with or without label
        super().endBlock(rank, label)


class Label(ProtonabuParsingStack.Stackable):
    """ Stackable Label
        - Purpose: Abstract node in Protonabu Schema
    """
    class Tokenizer:
        """ Label Tokenizer
            - Purpose: Tokenizer wrapper for Label
        """
        def __init__(self, func: ITokenizer, isMandatory: bool, name: str):
            """ to INITIALIZE Label Tokenizer
                - Input: to parse label
                - Input: is Mandatory
                - Input: name
            """
            self.func: ITokenizer = func
            self.isMandatory: bool = isMandatory
            self.name: str = name

        def __str__(self):
            """ to get label as string
                - Output: label string
            """
            return f"{self.name}{'' if self.isMandatory else '?'}"

    def __init__(self,
        name: str = "",
        labelModifierTokenizer: Optional[Label.Tokenizer] = None,
        argumentTokenizer: Optional[Label.Tokenizer] = None,
        argModifierTokenizer: Optional[Label.Tokenizer] = None
    ):
        """ to INITIALIZE Stackable Label
            - Input: name
            - Input [Opt "None"]: label Modifier Tokenizer
            - Input [Opt "None"]: argument Tokenizer
            - Input [Opt "None"]: arg Modifier Tokenizer
        """
        super().__init__()
        self.name: str = name
        # Contains [1:0-N By Value]: Stackable Label [role "token list"]
        self.tokenList: list[Label] = []
        # Contains [1:1 By Reference]: Stackable Label [role "label"]
        self.label: Label = self
        # Contains [1:0-1 By Value]: Label Tokenizer [role "label modifier tokeniser"]
        self.labelModifierTokenizer: Optional[Label.Tokenizer] = labelModifierTokenizer
        # Contains [1:0-1 By Value]: Label Tokenizer [role "argument tokeniser"]
        self.argumentTokenizer: Optional[Label.Tokenizer] = argumentTokenizer
        # Contains [1:0-1 By Value]: Label Tokenizer [role "argument modifier tokeniser"]
        self.argModifierTokenizer: Optional[Label.Tokenizer] = argModifierTokenizer
        self.function: str = ''
        self.isCollected: bool = False

    def getChildren(self) -> list[Label]:
        """ to get children of Stackable <Label>
            - Output: list of Stackable objects
        """
        return self.tokenList

    def append(self, label: "Label"):
        """ to add parse tree node
            - Input: Label
        """
        self.tokenList.append(label)

    def availTokens(self) -> list[str]:
        """ to collect all available Child label names under label
            - definitive
            - Output: litterals
        """
        # [Scan "self"]: to pick label name
        return [x.name for x in self]

    def availTokensExplicit(self) -> list[str]:
        """ to collect all (explicitly) available child label names under label
            - Output: litterals
        """
        # [Scan; Opt]: to pick from token List of self (protonabu Schema at 0133)
        return [x.name for x in self.tokenList if x.name]

    def findChildLabel(self, name: str) -> Optional["Label"]:
        """ to find sub-label by name
            - Input: label name
            - Output: sub-label
        """
        return next((x for x in self if x.name == name), None)

    def __getitem__(self, key: str) -> "Label":
        """ to get Sub-label
            - Input: key
            - Output: Sub-label
        """
        child = next((x for x in self.tokenList if x.name == key), None)
        # [Esc Error]: child not found
        if not child:
            raise IndexError(f'key {key} is not in control attributes')
        return child

    def __iter__(self) -> Iterator["Label"]:
        """ to TRAVERSE <SUBSTITUTE> Stackable Label
            - Output: Label iterator
            - definitive [Part]
        """
        # [Scan]: to extract child Label
        for child in self.tokenList:
            # [Alt "Named"]: to extract child Label
            if child.label.name:
                yield child
            # [Alt "unnamed"]: to TRAVERSE <SUBSTITUTE> Stackable Label
            else:
                yield from child

    def tellQuantity(self) -> str:
        """ to tell label quantity
            - Output: label quantity
        """
        return ''

    def dumpNode(self, 
        visited: list["Label"],
        outp: TextIO,
        level: int,
        index: dict[str, "Label"]
    ):
        """ to dump <SUBSTITUTE> Stackable Label node
            - Input: visited
            - Input: output file
            - Input: level
            - Input: index
        """
        # [Scan]: to dump schema entry
        for child in self.tokenList:
            # [Alt "Named"]: to dump named Stackable Label
            if child.name:
                outp.write('    ' * level)
                outp.write(child.name)
                # [Opt]: to dump Stackable Label modifier token
                if child.labelModifierTokenizer:
                    outp.write(f' [{str(child.labelModifierTokenizer)}]')
                # [Opt]: to dump argument token
                if child.argumentTokenizer:
                    outp.write(f': {str(child.argumentTokenizer)}')
                    # [Opt]: to dump argument modifier token
                    if child.argModifierTokenizer:
                        outp.write(f' [{str(child.argModifierTokenizer)})]')
                outp.write('\n')
                # [Esc Once]: recursive traversal
                if child in visited: continue
                visited.append(child)
                # [Msg]: to dump <SUBSTITUTE> Stackable Label node
                child.dumpNode(visited, outp, level+1, index)
            # [Alt "unnamed"]: to dump <SUBSTITUTE> Stackable Label node
            else:
                child.dumpNode(visited, outp, level, index)


class DittoLabel(Label):
    """ Ditto Stackable Label
        - Purpose: Ditto Subtree in Protonabu Schema
    """

    def __init__(self, aLabel: Optional["Label"] = None):
        """ to INITIALIZE Ditto Stackable Label
            - Input [Opt]: Ditto Stackable Label
        """
        # [Msg]: to INITIALIZE Label
        super().__init__()
        # [Opt Ditto Label]: to append label to token list
        if aLabel:
            # to add parse tree node
            # - Using: aLabel
            self.append(aLabel)

    def set(self, aLabel: "Label"):
        """ to set Ditto Stackable Label
            - Input: Ditto Stackable Label
        """
        self.tokenList = [aLabel]

    def __iter__(self) -> Iterator["Label"]:
        """ to TRAVERSE <Ditto> Stackable Label
            - Output: label iterator
            - definitive [Part]
        """
        # [Scan]: to Extract grandchild label
        for grandchild in self.tokenList[0]:
            yield grandchild

    def dumpNode(self, 
        visited: list["Label"],
        outp: TextIO,
        level: int,
        index: dict[str, "Label"]
    ):
        """ to dump <DITTO> Stackable Label Node
            - Input: visited
            - Input: output file
            - Input: level
            - Input: index
        """
        # [Esc Done]: empty token list
        if not self.tokenList: return
        offset = '    ' * level
        # to find label-reference path
        path = [x[0] for x in index.items() if x[1] == self.tokenList[0]][0]
        # [Msg]: to dump Ditto Stackable schema entry
        outp.write(f'{offset}__DITTO__: {path}\n')


class ProtonabuSchema:
    """ Protonabu Schema
    """
    comment = '//'
    endToken = 'END'

    def __init__(self,
         inp: ProtonabuSnippet,
         additionalTokenizerModules: Optional[list[ModuleType]] = None
    ):
        """ to INITIALIZE Protonabu Schema
            - Exported
            - Input: protonabu snippet
            - Input [Opt]: additional tokenizer modules
        """
        # Contains [1:1 by Value]: Stackable Label [role "root label"]
        self.rootLabel = Label('')
        # Contains [0-N by Value]: Stackable Label [role "root list"]
        self.rootList: list[Label] = self.rootLabel.tokenList
        self.name: str = ''
        # Contains [0-N by Reference]: Stackable Label [role "index"]
        # - Key: label name
        self.index: dict[str, Label] = {}
        # Contains [0-N by Value]: Stackable Label [role "templates"]
        # - Key: label name
        self.templates: list[Label] = []
        # Contains [0-N by Reference]: Ditto Stackable Label [role "nameWatchers"]
        # - Multikey: label name
        self.nameWatchers: dict[str, list[DittoLabel]] = defaultdict(list)
        # Contains [1:1 by Value]: Protonabu Snippet [role "inp"]
        self.inp = inp
        # Contains [1:1 by Value]: Schema Parsing Stack [role "stack"]
        self.stack = SchemaParsingStack()
        # [Msg]: to update Schema Parsing Stack
        self.stack.update(0, "", self.rootLabel)
        # Contains [1:0-N By Reference]: Tokenizer Interface
        self.tokenizers: dict[str, ITokenizer] = {}
        self.immediateDirectives: list[str] = []
        self.recursiveLabels: list[str] = []
        self.unicodeLabels: list[str] = []
        self.labels: set[str] = set([])
        self.tokenizerModules: list[ModuleType] = [primitiveTokens, tokenizedFact]
        # [Opt]: to add user-supplied tokenizer modules to schema
        if additionalTokenizerModules:
            self.tokenizerModules += additionalTokenizerModules
        # [Guard]: to parse Schema tree
        try:
            self.__parse()
        # [Esc Error]: Abort
        except FactFileError:
            raise

    def append(self, label: "Label"):
        """ to add root node
            - Input: Label
        """
        self.rootList.append(label)

    def availTokens(self) -> list[str]:
        """ to collect all available Child label names under schema root
            - Output: litterals
        """
        # [Scan "root list"]: to get label name
        return [x.name for x in self.rootList]

    def findChildLabel(self, name: str) -> Optional["Label"]:
        """ to find root label by name
            - Input: label name
            - Output: sub-label
        """
        return next((x for x in self.rootList if x.name == name), None)

    @staticmethod
    def load(fileName):
        """ to parse Protonabu syntax tree
            - Exported
            - definitive [Part]
            - Input: file Name
            - Output: result
        """
        # [Msg]: to INITIALIZE Protonabu Schema from file
        # - Using:  to create Protonabu Snippet from file
        result = ProtonabuSchema(
            snippet := ProtonabuSnippetFromFile(fileName)
        )
        # [Msg]: to close Protonabu Snippet
        snippet.close()
        return result

    def getNode(self, fullLabel: str) -> Optional["Label"]:
        """ to get Label
            - Input: full Label name
            - Output [Opt]: child Label
        """
        # [Guard]: to get label from schema index
        try:
            return self.index[fullLabel]
        # [Esc Error]: "KeyError"
        except KeyError: 
            return None

    def dump(self, outp: Optional[TextIO] = None):
        """ to dump Protonabu Schema
            - Exported
            - Input [Opt]: output stream
        """
        # [Opt]: to direct Protonabu schema dump to the terminal
        if not outp:
            outp = sys.stdout
        outp.write('__SCHEMA_SECTION__: TOKENS\n')
        # [Msg]: to dump the Parse Tree
        self.rootLabel.dumpNode([], outp, 0, self.index)

    def __parse(self):
        """ to parse Schema tree 
            - definitive 
        """
        # to parse Schema tree entry
        parsers: dict[str, Callable[[RawFact], None]] = {
            'IMMEDIATE':  self.__parseImmediate,
            'TOKENS':     self.__parseEntry
        }
        # to prepare to parse schema tokens section
        self.currentSection = 'TOKENS'
        currentParser = parsers[self.currentSection]
        # [Guard; Scan]: to parse schema facts
        try:
            for rawFact in self.inp:
                # [Esc]: schema section
                if rawFact.label == '__SCHEMA_SECTION__':
                    # [Esc Error]: invalid schema section
                    if rawFact.arg.upper() not in parsers:
                        raise Error('Invalid schema section', [('Section', rawFact.arg)])
                    self.currentSection = rawFact.arg.upper()
                    currentParser = parsers[self.currentSection]
                    continue
                # [Msg]: to parse rawFact in schema section
                currentParser(rawFact)                                                                                                                                                                                                                                                              
        # [Esc Error]: Fact File error
        except FactFileError:
            raise
        # [Esc Error]: Fact File Error
        except Error as exp:                                                                                                                                                                
            raise FactFileError(
                self.inp.fileName, 
                self.inp.lineNum, 
                exp.message, 
                fields=exp.fields
            )
        # [Esc Error]: Ditto references not exhausted
        if self.nameWatchers:
            raise Error('Composite Fact schema error: Unresolved references in parse tree', [
                ('Reference', first(self.nameWatchers))
            ])
        # [Scan]:to remove immediate directives from labels
        for label in self.immediateDirectives:
            with suppress(KeyError):
                self.labels.remove(label)

    def __parseImmediate(self, rawFact: RawFact):
        """ to parse immediate schema fact
            - Input: raw Fact
        """
        # [Opt]: to add immediate directive to list
        if rawFact.label not in self.immediateDirectives:
            self.immediateDirectives.append(rawFact.label)

    def __parseEntry(self, rawFact: RawFact):
        """ to parse schema fact
            - Input: raw Fact
        """
        def parseArg(arg: str) -> tuple[str, bool]:
            """ to parse schema fact argument
                - Input: argument string
                - Output: full argument
                - Contains: argument
                - Contains: is mandatory
            """
            # [Esc Done]: Optional argument
            if arg.endswith('?'):
                return arg[:-1], False
            return arg, True

        isRef = False
        labelModifier: tuple[str, bool] = '', False
        argument: tuple[str, bool] = '', False
        argModifier: tuple[str, bool] = '', False
        # [Esc]: "ditto fact"]: to parse ditto schema fact
        if rawFact.label == '__DITTO__':
            # [Esc]: no argument
            if not rawFact.arg:
                raise FactFileError(
                    self.inp.fileName, 
                    self.inp.lineNum, 
                    'Protonabu schema error: invalid schema ditto fact'
                )
            # [Msg]: to parse design path
            pathTokens = primitiveTokens.designPath.parseString(rawFact.arg, parseAll=True).asList()
            pathList = tokenizedFact.parseDesignPath(
                tokenizedFact.TokenListIterator(pathTokens)
            )
            label = ' / '.join(pathList)
            isRef = True
        # [Alt "schema token fact"]: to parse schema token fact
        else:
            label = rawFact.label
            # [Opt]: to parse schema fact label modifiers
            # - Using: Label modifier
            if rawFact.labelModifiers:
                # to parse schema fact argument
                # - Using: first label modifier
                labelModifier = parseArg(rawFact.labelModifiers[0]) # todo...
            # [Opt]: to parse schema fact argument and modifier
            if rawFact.arg:
                # [Msg]: to parse schema fact argument
                # - Using: Argument
                argument = parseArg(rawFact.arg)
                # [Msg; Opt]: to parse schema fact argument modifier
                # - Using: Argument modifier
                if rawFact.argModifiers:
                    # [Msg]: to parse schema fact argument
                    argModifier = parseArg(rawFact.argModifiers[0]) # todo...
        # [Msg]: to parse Protonabu schema Label
        label = self.__parseLabel(
            label,
            labelModifier,
            argument,
            argModifier,
            isRef,
            rawFact.rank,
            rawFact.comment
        )
        # [Opt "schema token fact"]: to add label to labels set
        if self.currentSection == 'TOKENS' and not isRef:
            self.labels.add(label)

    def __parseLabel(self,
        sLabel: str,
        labelModifier: tuple[str, bool],
        argument: tuple[str, bool],
        argModifier: tuple[str, bool],
        isRef: bool,
        rank: int,
        function: str
    ):
        """ to parse Protonabu schema Label
            - Input: label string
            - Input: label modifier
            - Input: argument
            - Input: argument modifier
            - Input: is ditto reference
            - Input: rank
            - Input: function
            - Output: label string
        """
        def addTokenizer(
            tokenizerName: str,
            isMandatory: bool = True
        ) -> Optional[Label.Tokenizer]:
            """ to find tokenizer function by name in search libraries
                - Input: tokenizer name
                - Input: is mandatory
                - Output: tokenizer function
            """
            # [Esc Error]: tokenizer name not given
            if not tokenizerName: 
                # [Esc Done]: optional tokenizer missing
                if not isMandatory: return None
                raise Error("Protonabu schema error: Invalid tokenizer name", [
                    ('Token', tokenizerName)
                ])
            tokenizerFunc = None
            # [Guard]: to retrieve schema tokenizer
            try:
                tokenizerFunc = self.tokenizers[tokenizerName]
            # [Esc Error]: tokenizer not found
            except KeyError:
                # [Scan tokenizer modules]: to search for tokenizer in tokenizer modules
                for lib in self.tokenizerModules:
                    with suppress(AttributeError):
                        # [Msg]: to retrieve tokenizer from module
                        tokenizerFunc = getattr(lib, tokenizerName)
                        # to auto-register tokenizer
                        self.tokenizers[tokenizerName] = tokenizerFunc
                        break
                # [Esc Error]: tokenizer not found
                if not tokenizerFunc:
                    raise Error("Protonabu schema error: Missing tokenizer", [('Token', tokenizerName)])
            # [Msg]: to INITIALIZE Label Tokenizer
            return Label.Tokenizer(tokenizerFunc, isMandatory, tokenizerName)

        # [Alt label]: to INITIALIZE Stackable Label
        if not isRef:
            child = Label(
                sLabel,
                addTokenizer(*labelModifier),
                addTokenizer(*argument),
                addTokenizer(*argModifier)
            )
        # [Alt "Ditto"]: to parse Ditto Label
        else:
            child = self.__parseDittoLabel(sLabel)
        child.function = function
        # [Msg]: to update Schema Parsing Stack
        self.stack.update(rank, sLabel, child)
        # [Msg; Opt]: to prepare for recursive label
        if (
            sLabel not in self.recursiveLabels
            and [x[1].name for x in self.stack.ranks if x[1] and x[1].name].count(sLabel) == 2
        ):
            self.recursiveLabels.append(sLabel)
        # [Opt]: to add current node to parse tree index
        if child.name:
            # [Msg]: to add the current node to the Parse Tree index
            self.__indexNode(child)
        # [Opt]: to update the parse tree
        if (parent := self.stack.getParent()) is not None:
            parent.append(child)
        # [Esc Error]: Misplaced token
        if (
            (parent := self.stack.getParent()) is not None
            and not parent.name
            and self.stack.getRank() > 1
        ):
            raise FactFileError(
                self.inp.fileName, 
                self.inp.lineNum, 
                f'Protonabu schema error: parse-tree entry under reference {sLabel}'
            )
        return sLabel

    def __indexNode(self, child):
        """ to add the current node to the Parse Tree index
            - Input: child node
        """
        # to build the current full schema path
        fullName = ' / '.join([
            x[1].name 
                for x in self.stack.ranks 
                    if x[1] and x[1].name
        ])
        # [Esc Error]: duplicate parse tree entry
        if fullName in self.index:
            raise FactFileError(
                self.inp.fileName, 
                self.inp.lineNum, 
                f'Protonabu schema error: duplicate parse-tree entry {fullName}'
            )
        self.index[fullName] = child
        with suppress(KeyError):
            # [Msg; Scan]: to set Ditto Label
            for watcher in self.nameWatchers[fullName]:
                watcher.set(child)
            # [Msg]: to forget Schema path name watcher
            self.nameWatchers.pop(fullName)

    def __parseDittoLabel(self, token) -> DittoLabel:
        """ to parse Ditto Label
            - Input: token
            - Output: Ditto Label
        """
        # to build the current full schema path
        path = ' / '.join([
            x[1].name for x in self.stack.ranks if x[1] and x[1].name]
        )
        # [Esc Error]: recursive reference in syntax tree
        if token == path:
            raise Error('Protonabu schema error: recursive reference in syntax tree', [
                ('reference', token)
            ])
        # [Guard]: to retrieve label from index
        try:
            ref = self.index[token]
        # [Esc Ignore]: not found
        except KeyError:
            ref = None
        # [Msg]: to INITIALIZE Ditto Label
        child = DittoLabel(ref)
        # [Opt]: to add label to name watchers
        if not ref:
            self.nameWatchers[token].append(child)
        return child
        
