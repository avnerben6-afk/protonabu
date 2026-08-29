""" Module: Protonabu Parser Module
    - Author: Avner Ben
        - Created: 23-Jun-2026
            - Separated from Fact Snippet Parser
        - Improved: 23-Aug-2026
          - Prepared for release
    - Generator: Antigravity (Gemini 3.7 Flash)
        - Improved: 25-Aug-2026
"""

from types import ModuleType
from pyparsing import ParseException
import sys
from pathlib import Path
from contextlib import suppress
from abc import ABC, abstractmethod
from typing import Any, Iterator, Optional, Callable

from .util.error import Error, InternalError, FactFileError
from .util.stringUtil import unquote, unCamel
# [Additional]
from .util.progress import IProgressIndicator, DummyProgressIndicator
# [Additional]
from .rawFact import RawFact, ProtonabuParsingStack
# [Additional]
from .tokenizedFact import (
    TokenizedFact, 
    TokenListIterator
)
# [Additional]
from .factSnippet import (
    ProtonabuSnippet, 
    ProtonabuSnippetFromFile,
    ProtonabuSnippetInMemory
)
# [Additional]
from .protonabuSchema import (
    ProtonabuSchema,
    Label
)


class SnippetParser:
    """ Snippet Parser
        - Purpose: to tokenize Protonabu Fact from snippet
    """
    class TokenList(ProtonabuParsingStack.Stackable):
        """ Stackable Token List
            - Purpose: a Protonabu Fact snippet line, tokenized and ready to parse
        """
        def __init__(self, line: Optional[TokenizedFact], label: Optional[Label]):
            """ to INITIALIZE Stackable Token List
                - Input: line
                - Input: label
            """
            super().__init__()
            # Contains [1:1 By Value]: Tokenized Fact [Role "line"]
            self.line: Optional[TokenizedFact] = line
            # Contains [1:0-N By Value]: Stackable Token List [Role "children"]
            self.children: list[SnippetParser.TokenList] = []
            # Contains [1:1 By Value]: Stackable Label [Role "label"]
            self.label: Optional[Label] = label
            self.isPending = True

        def getChildren(self) -> list[SnippetParser.TokenList]:
            """ to get children of Stackable <Token List>
                - Output: list of Stackable objects
            """
            return self.children

        def __iter__(self) -> Iterator["SnippetParser.TokenList"]:
            """ to TRAVERSE Stackable Token List
                - Output: result
                - definitive [Part]
            """
            return iter(self.children)


    class FactParsingPath:
        """ Fact Parsing Path
        """
        class Entry:
            """ Fact Parsing Path Entry
            """
            def __init__(self,
                label: str,
                memento: Optional[Any] = None
            ):
                """ to INITIALIZE Fact Parsing Path Entry
                    - Input: label
                    - Input [Opt "None"]: memento
                """
                self.label: str = label
                self.memento: Optional[Any] = memento

            def __iter__(self) -> Iterator[str | Any]:
                """ to TRAVERSE Fact Parsing Path Entry
                    - Motivation: Compatibility with obsolete tuple implementation
                    - Output: result
                    - definitive [Part]
                """
                yield self.label
                yield self.memento

            def asTuple(self) -> tuple[str, Any]:
                """ to convert Fact Parsing Path Entry to tuple
                    - Output: label and memento
                """
                return self.label, self.memento

        def __init__(self,
             path: Optional["SnippetParser.FactParsingPath"] = None,
             entry: Optional[Entry] = None,
             pos: int = 0,
             children: Optional[list["SnippetParser.TokenList"]] = None
        ):
            """ to INITIALIZE Fact Parsing Path
                - Input [Opt "None"]: Fact Parsing Path
                - Input [Opt "None"]: Fact Parsing Path Entry
                - Input [Opt "0"]: index
                - Input [Opt "None"]: children
            """
            # Contains [1:0-N By Value]: Fact Parsing Path Entry [Role "entries"]
            self.entries: list[SnippetParser.FactParsingPath.Entry] = []
            # [Opt]: to copy given path to Fact Parsing Path Entry
            if path:
                self.entries = path.entries[:]
            # [Opt]: to add the current entry to Fact Parsing Path Entry
            if entry:
                self.entries.append(entry)
            self.pos: int = pos
            # Contains [1:0-N By Reference]: Stackable Token List [Role "children"]
            self.children: list[SnippetParser.TokenList] = children if children else []

        def setChildren(self, children: list["SnippetParser.TokenList"]):
            """ to set children of Fact Parsing Path Entry
                - Input: children
                - definitive [Part]
            """
            self.children = children

        def asList(self) -> list[tuple[str, Any]]:
            """ to convert Fact Parsing Path Entry to list
                - Output: entry list
                - Contains: entry
                - Contains: label
                - Contains: memento
            """
            # [Msg; Scan]: to convert Fact Parsing Path Entry to tuple
            return [x.asTuple() for x in self.entries]

        def incPos(self):
            'to increment parse node position'
            self.pos += 1

    def __init__(self, schema: ProtonabuSchema):
        """ to INITIALIZE Protonabu Tokenizer
            - Input: schema
        """
        # Contains [1:1 By Value]: Protonabu Schema [Role "schema"]
        self.schema: ProtonabuSchema = schema
        # Contains [1:0-N by Value]: Labeled Fact Parser  
        # - key: "label"
        self.immediateHandlers: dict[str, Callable[[TokenizedFact, Iterator[RawFact]], None]] \
            = {self.schema.endToken: self.parseEnd}
        # Contains [1:1 By Value]: Protonabu Parsing Stack [Role "stack"]
        self.stack = ProtonabuParsingStack()
        # Contains [1:1 By Value]: Stackable Token List [Role "frames"]
        self.frames = self.TokenList(None, self.schema.rootLabel)
        # [Msg]: to update the rank stack
        self.stack.update(0, "", self.frames)
        self.numFrames = 0
        # [Scan; Opt]: to pick matchinglabel from schema index
        # - Giving [to append]: labels
        self.labels: list[str] = [
            x for x in {x.rsplit('/', 1)[-1].strip() for x in schema.index}
            if x.upper() == x
        ]
        self.pendingLabel: Optional[str] = None
        # Contains [1:0-1 By Value]: Protonabu Snippet [Role "input"]
        self.inp: Optional[ProtonabuSnippet] = None
        self.currentRank1: tuple[str, str] = '', ''
        self.exitValidators: dict[Any, Callable[[Any], None]] = {}

    def compile(self, 
        inp: ProtonabuSnippet, 
        progressBar: Optional[IProgressIndicator]=None
    ):
        """ to compile <SUBSTITUTE Snippet> Parser source
            - definitive [Part]
            - Input: input labeld fact snippet
            - Input [Opt "None"]: a progress indicator
        """
        # [Opt]: to INITIALIZE dummy progress indicator
        aProgressBar = progressBar or DummyProgressIndicator()
        self.inp: ProtonabuSnippet = inp
        # [Msg]: to collect immediate directive labels
        immediateLabels = list(self.immediateHandlers.keys())
        # [Scan]: to validate immediate label
        for token in self.schema.immediateDirectives:
            # [Esc Error]: token not in immediate Labels
            if token not in immediateLabels:
                raise Error(
                    'Composite Fact schema error: Missing parser for immediate directive',
                    [('Directive', token)]
                )
        aProgressBar.start()
        # to allow the line stream access to the parsing stack
        inp.parsingStack = self.stack
        # [Msg]: to TRAVERSE <SUBSTITUTE> Fact Stream
        itr = iter(self.inp)
        # [Guard]: to to compile substitute snippet parser source (protonabu Parser at 0210)
        try:
            # [Rpt "While raw facts"]: to tokenize raw fact from snippet
            while True:
                # [Guard]: to extract next raw fact from snippet iterator
                try:
                    rawFact = next(itr)
                # [Esc Done]: End of iteration
                except StopIteration: break
                
                # [Esc]: is Cancelled of a Progress rest
                if aProgressBar.isCancelled():
                    raise Error('Cancelled by user')
                
                # [Msg]: to update progress indicator
                aProgressBar.progress()
                # [Esc Done]: immediate directive label
                if rawFact.label in immediateLabels:
                    # [Msg]: to INITIALIZE Tokenized Fact
                    aFactParser = TokenizedFact(
                            rawFact,
                            [rawFact.label],
                            rawFact.rank,
                            rawFact.fileName,
                            rawFact.lineNumber,
                            isImporting = rawFact.isImporting
                    )
                    # [Guard]: to parse immediate directive fact
                    try:
                        # [Msg]: to parse immediate directive fact
                        self.immediateHandlers[rawFact.label](aFactParser, itr)
                        continue
                    # [Esc Error]: "Fact File Error"
                    except Error as err:
                        raise FactFileError(
                            aFactParser.fileName, 
                            aFactParser.lineNum, 
                            getattr(err, 'origMessage', err.message),
                            fields=getattr(err, 'fields', None)
                        )
                self.currentRawFact = rawFact
                # [Guard]: to tokenize the current labeled fact
                try:
                    # [Msg]: to update the rank stack
                    self.stack.update(rawFact.rank, '', None)
                    # [Msg]: to get parent of current indented object
                    parent = self.stack.getParent()
                    # [Esc Error]: Missing parent frame
                    if parent is None or parent.label is None:
                        raise Error('Invalid fact level: missing parent container', [
                            ('Label', rawFact.label),
                            ('Rank', rawFact.rank)
                        ])
                    # [Msg]: to INITIALIZE Tokenized Fact
                    aFactParser = TokenizedFact(
                        rawFact,
                        parent.label.availTokens(),
                        rawFact.rank,
                        rawFact.fileName,
                        rawFact.lineNumber,
                        isImporting = rawFact.isImporting
                    )
                # [Esc Error]: "Tokenizing error"
                except Error as err:
                    path = ' / '.join([x[0] for x in self.stack.ranks if x[0]])
                    if path:
                        err.set('Path', path)
                    raise err
                # [Guard]: to push Protonabu parsing frame
                try:
                    # [msg]: to find sub-label by name
                    child = parent.label.findChildLabel(aFactParser.label)
                    # [Esc Error]: "Unexpected label"
                    if not child:
                        raise Error('Unexpected label!', [
                            ('Label', aFactParser.label),
                            ('Path',  ' / '.join([x[0] for x in self.stack.ranks if x[0]]))
                        ])
                    # [msg]: to INITIALIZE Stackable Token List
                    # - Giving: The current parsing frame
                    frame = self.TokenList(aFactParser, child)
                    self.numFrames += 1
                    self.stack.ranks[-1] = aFactParser.label, frame
                    parent.children.append(frame)
                    # [Opt]: to remenber the first parsing frame
                    if rawFact.rank == 1:
                        self.currentRank1 = rawFact.label, unquote(rawFact.arg)
                # [Esc Error]: "Fact File Error"
                except FactFileError:
                    raise
                # [Esc Error]: "Nabu Error"
                except Error as err:
                    s1 = getattr(err, 'origMessage', str(err)) if aFactParser.label else 'missing line type'
                    parent = self.stack.getParent()
                    s2 = parent.label.name if parent and parent.label and getattr(parent.label, 'name', None) else ''
                    s2 = f'Under: {s2}' if s2 else 'at level zero'
                    raise FactFileError(
                        aFactParser.fileName, 
                        aFactParser.lineNum, 
                        f'{s1}\n{s2}',
                        fields=getattr(err, 'fields', None)
                    )
        finally:
            # [Msg]: to close progress indicator
            aProgressBar.end()

    def parseEnd(self,
        lineData: TokenizedFact,
        _: Optional[Iterator[RawFact]]
    ):
        """ to end labeled-fact tokenization
            - Input: line Data
            - Input: itr
        """
        self.stack.endBlock(
            lineData.indent,
            lineData.rawFact.arg.upper()
        )

    def parseLines(self,
        aLineParser: "ProtonabuParseDispatcher",
        aProgressBar: Optional[IProgressIndicator]=None
    ):
        """ to parse tokenized Labeled Fact source
            - Input: Line Parser
            - Input [Opt "None"]: Progress Bar
            - Purpose: to perform semantic analysis and domain object generation.
            - Method: to recursively traverse the token tree built by compile and dispatch the tokenized facts
            to the line parsers, probably triggering handlers that build domain elements
            - definitive 
        """
        lastFileName = ''
        def walk(
            frame: SnippetParser.TokenList,
            path: SnippetParser.FactParsingPath
        ):
            """ to process tokenized composite Labeled Fact
                - Input: tokenized composite fact
                - Input: design path
            """
            nonlocal lastFileName
            # [Scan "frame"]: to process tokenized composite Labeled Fact and children
            for fact in frame:
                # [Esc]: is Cancelled of a Progress rest
                if aProgressBar.isCancelled():
                    raise Error('Cancelled by user')
                # [Guard]: to do process tokenized composite Labeled Fact and children
                try:
                    label_node = fact.label
                    # [Esc Error]: "Corrupted AST: missing schema Label"
                    if label_node is None:
                        file_name = fact.line.fileName if fact.line else '<unknown>'
                        line_num = fact.line.lineNum if fact.line else '?'
                        fact_label = fact.line.label if fact.line else '<unlabeled>'
                        raise InternalError(
                            'Corrupted AST node: missing schema Label',
                            [('Label', fact_label), ('File', file_name), ('Line', line_num)]
                        )
                    label = label_node.name
                    # [Esc Ignored]: "Label Pending"
                    if self.pendingLabel:
                        # [Esc Error]: "Wrong label pending"
                        if label != self.pendingLabel:
                            raise Error('Expected label', [('Expected', self.pendingLabel)])
                        # to reset pending label
                        self.pendingLabel = None
                    # [Esc Error]: "Corrupted AST: missing line data"
                    if fact.line is None:
                        raise InternalError(
                            'Corrupted AST node: missing line data',
                            [('Label', label), ('File', '<unknown>'), ('Line', '?')]
                        )
                    fact_line = fact.line
                    # [Opt]: to indicate Fact as the first
                    if fact_line.fileName != lastFileName: # todo: reconsider usefulness!
                        # to set last file name parsed
                        lastFileName = fact_line.fileName
                        fact_line.isFirst = True
                    # [Msg]: to set children of Fact Parsing Path Entry
                    path.setChildren(fact.children)
                    # [Msg]: to increment current position
                    path.incPos()
                    # [Msg]: to progress progress indicator
                    aProgressBar.progress()
                    # [Msg]: to dispatch Protonabu Fact parsing
                    memento: Any = aLineParser.beginItem(
                        # - Using: Tokenized Fact 
                        fact_line,
                        # - Using: Design Path
                        path,
                        # - Using: label Modifier Tokenizer
                        label_node.labelModifierTokenizer,
                        # - Using: argument Tokenizer
                        label_node.argumentTokenizer,
                        # - Using: arg Modifier Tokenizer
                        label_node.argModifierTokenizer
                    )
                    # [Opt]: to process tokenized composite Labeled Fact
                    if len(fact.children):
                        # [Msg]: to [Using; Using]: to walk
                        walk(fact, self.FactParsingPath(path, self.FactParsingPath.Entry(label, memento))) 
                    aLineParser.endItem(fact_line)
                # [Esc Error]: "Fact File Error"
                except (FactFileError, InternalError):  
                    raise
                # [Esc Error]: "Generic Nabu Error"
                except Error as error:
                    file_name = fact.line.fileName if fact.line else '<unknown>'
                    line_num = fact.line.lineNum if fact.line else '?'
                    raise FactFileError(file_name, line_num, getattr(error, 'origMessage', error.message), fields=getattr(error, 'fields', None))

        # [Opt]: to INITIALIZE dummy progress indicator
        if not aProgressBar:
            # [Msg]: to INITIALIZE dummy progress indicator
            aProgressBar = DummyProgressIndicator()
        # [Msg]: to start progress indicator
        aProgressBar.start()
        # [Guard]: to to parse tokenized labeled fact source (protonabu Parser at 0397)
        try:
            # [Msg]: to process tokenized composite Labeled Fact
            # - Using: Tokenized Fact AST root
            # - Using: Fact Parsing Path
            walk(self.frames, self.FactParsingPath())
            # [Scan]: to validate parsed token at exit
            for obj, validator in self.exitValidators.items():
                # [Msg]: to [Using]: to validator
                validator(obj)
        finally:
            # [Msg]: to end progress indicator
            aProgressBar.end()

    def dump(self, outp=None):
        """ to dump composite Labeled Fact for debug
            - Input [Opt "None"]: output stream
        """
        offset, sep = '    ', '; '

        def walk(innerFrame: "SnippetParser.TokenList", rank):
            """ to recurse entry
            """
            labelName = innerFrame.label.name if innerFrame.label and getattr(innerFrame.label, 'name', None) else (innerFrame.line.label if innerFrame.line else '')
            line = f'{offset * rank}{labelName}'
            if innerFrame.line and innerFrame.line.rawFact:
                # [Opt]: to prepare to dump tokenized label modifiers
                if modifiers := innerFrame.line.rawFact.labelModifiers:
                    line += f' [{sep.join(modifiers)}]'
                # [Opt]: to prepare to dump tokenized fact argument
                if innerFrame.line.rawFact.arg:
                    line += f': {innerFrame.line.rawFact.arg}'
                    # [Opt]: to prepare to dump tokenized argument modifiers
                    if modifiers := innerFrame.line.rawFact.argModifiers:
                        line += f' [{sep.join(modifiers)}]'
            outp.write(line + '\n')
            # [Scan "children"]: to dump composite Labeled Fact for debug
            # - Using: child
            for childFrame in innerFrame.children:
                # [Msg]: to [Using; Using]: to walk
                walk(childFrame, rank + 1)

        # [Opt]: to direct Protonabu Parser dump to console
        if not outp:
            outp = sys.stdout
        # [Scan "frames"]: to dump composite Labeled Fact for debug
        # - Using: frame
        for frame in self.frames:
            # [Msg]: to [Using; Using]: to walk
            walk(frame, 0)

    def registerExitValidator(self, obj: Any, validator: Callable[[Any], None]):
        """ to defer parsed-object validation to fact-base completion
            - Input: object to validate
            - Input: validator method
            - Reason: to defer parsed-object validation where that requires waiting for the fact-base to be complete
            - definitive
        """
        self.exitValidators[obj] = validator

    def unregisterExitValidator(self, obj: Any):
        """ to forget parsed-object deferred validation
            - Input: object to stop validating
        """
        # [Guard]: to forget parsed-object deferred validation
        try:
            self.exitValidators.pop(obj)
        # [Esc Error]: "error"
        except KeyError: pass


class ProtonabuParseDispatcher:
    """ Protonabu Fact parse Dispatcher
        - Purpose: to dispatch Line Parser events to parse methods, by label
    """

    def __init__(self):
        """ to INITIALIZE Protonabu Parse Dispatcher
        """
        self.handlers: dict[
            str,                                          # label
            tuple[
                Callable[[TokenizedFact], Any],           # beginHandler
                Optional[Callable[[TokenizedFact], Any]]  # endHandler
            ]
        ] = {}

    def add(self,
        label: str,
        beginHandler: Callable[[TokenizedFact], Any],
        endHandler: Optional[Callable[[TokenizedFact], Any]] = None
    ):
        """ to register Protonabu Fact label parser
            - Input: label
            - Input: begin Handler
            - Input [Opt "None"]: end Handler
            - Output [state]: Handlers -- registered
        """
        label = label.upper()
        self.handlers[label] = beginHandler, endHandler

    def loadHandlers(self, 
        labels: set[str], 
        parser: object | ModuleType
    ): 
        """ to load handlers
            - Input: labels
            - Input: parser
        """
        # [Scan "labels"]: to find and register Labeled Fact line handler
        for label in labels:
            # [Esc Once]: already loaded
            if label in self.handlers: continue
            title = ''.join([x.capitalize() for x in label.split()])
            methodName = f'parse{title}'
            # [Esc Error]: method not found in parser
            if not hasattr(parser, methodName):
                raise Error('Protonabu schema error: Missing parser', [
                    ('Label', label)
                ])
            # to set parser handlers
            beginHandler, endHandler = getattr(parser, methodName), None
            endMethodName = f'{methodName}End'
            # [Opt]: to set end handler
            if hasattr(parser, endMethodName):
                endHandler = getattr(parser, endMethodName)
            self.handlers[label] = (beginHandler, endHandler)

    def beginItem(self,
        factParser: TokenizedFact,
        path,
        labelModifierTokenizer,
        argumentTokenizer,
        argModifierTokenizer
    ) -> list[Any]:
        """ to dispatch Fact Parsing
            - Input: fact Parser
            - Input: design path
            - Input: label Modifier Tokenizer
            - Input: argument Tokenizer
            - Input: arg Modifier Tokenizer
            - Output: result
            - Contains: Token List Iterator
            - definitive [Part]
        """
        def tokenizeModifiers(
                modifiers: list[str],
                tokenizer: Label.Tokenizer,
                errorName: str = 'modifier'
        ) -> list[TokenListIterator]:
            """ to tokenize modifier list
            """
            result: list[TokenListIterator] = []
            # to copy modifier list
            # [Scan]: to test modifier against candidate tokenizer
            for modifier in modifiers:
                # [Guard]: to tokenize Protonabu Fact element
                try:
                    result.append(
                        TokenListIterator(tokenizer.func.parseString(modifier, parseAll = True))
                    )
                # [Esc Error]: "invalid modifier"
                except ParseException:
                    raise Error(f'Invalid {errorName}!',[
                        ('Modifier', modifier),
                        ('Expected', unCamel(tokenizer.name))
                    ])
            # [Esc Error]: "Missing modifier"
            if not result and tokenizer.isMandatory:
                raise Error(f'Missing {errorName}!', [('Expected', unCamel(tokenizer.name))])
            return result

        # [Msg]: to retrieve begin and end parsers for action
        handlers = self.handlers.get(factParser.label, (None, None))
        # [Esc Error]: "missing line parser"
        if not handlers[0]:
            raise Error('Protonabu schema error: missing line parser for label', [('Label', factParser.label)])
        # [Guard]: to dispatch Fact Parsing
        try:
            # [Guard]: to do dispatch Fact Parsing
            try:
                # [Opt]: to dispatch the first line event handler
                if factParser.isFirst:  # todo: obsolete
                    with suppress(KeyError):
                        self.handlers['$FILE$'][0](factParser)
                # [Esc Error]: "Unexpected label modifier"
                if factParser.rawFact.labelModifiers and not labelModifierTokenizer:
                    raise Error('Unexpected label modifier', [
                        ('Label', factParser.label),
                        ('Modifier', factParser.rawFact.labelModifiers[0])
                    ])
                # [Opt]: to tokenize modifier list
                if labelModifierTokenizer:
                    # to [Using; Using; Using]: to tokenize modifiers
                    factParser.labelModifierTokenItrs = tokenizeModifiers(
                        factParser.rawFact.labelModifiers,
                        labelModifierTokenizer,
                        'label modifier'
                    )
                # [Esc Error]: "Unexpected argument"
                if factParser.rawFact.arg and not argumentTokenizer:
                    raise Error('Unexpected argument', [
                        ('Label', factParser.label),
                        ('Argument', factParser.rawFact.arg)
                    ])
                # [Esc]: argument Tokenizer
                if argumentTokenizer:
                    # [Esc Error]: "Missing argument"
                    if argumentTokenizer.isMandatory and not factParser.rawFact.arg:
                        raise Error('Missing argument', [
                            ('Label', factParser.label),
                            ('Expected', unCamel(argumentTokenizer.name))
                        ])
                    # [Opt]: to tokenize modifier list
                    if factParser.rawFact.arg:
                        factParser.argumentTokenItr = tokenizeModifiers(
                            [factParser.rawFact.arg],
                            argumentTokenizer,
                            'argument'
                        )[0]
                # [Esc Error]: "Unexpected argument modifier"
                if factParser.rawFact.argModifiers and not argModifierTokenizer:
                    raise Error('Unexpected argument modifier', [
                        ('Modifier', factParser.rawFact.argModifiers[0])
                    ])
                # [Opt]: to tokenize argument modifiers
                if argModifierTokenizer:
                    # to [Using; Using; Using]: to tokenize modifiers
                    factParser.argModifierTokenItrs = tokenizeModifiers(
                        factParser.rawFact.argModifiers,
                        argModifierTokenizer,
                        'argument modifier'
                    )
                factParser.designPath = path.asList()
                # [Guard]: to dispatch protonabu fact begin line parser
                try:
                    result = handlers[0](factParser)
                # [Esc Error]: "Key error in line parser"
                except KeyError as error:
                    handlerName = (
                        handlers[0].__name__ if hasattr(handlers[0], '__name__')
                        else 'unknown'
                    )
                    raise InternalError('Key error in line parser', [
                        ('Label', ' / '.join(
                            [x[0] for x in factParser.designPath + [(factParser.label, '')]])),
                        ('Parser', handlerName),
                        ('Line', factParser.lineNum),
                        ('Fact', factParser.rawFact.arg),
                        ('Error', str(error))
                    ])
                return result
            # [Esc Error]: "error"
            except KeyError:
                raise InternalError('Key error while dispatching line parser', [
                    ('Label', ' / '.join([
                        x[0] for x in factParser.designPath + [(factParser.label, '')]
                    ]))
                ])
        # [Esc Error]: "Some parsing error"
        except Error as err:
            # [Msg]: to append label path to parsing error
            err.set('Label', ' / '.join([
                x[0] for x in factParser.designPath + [(factParser.label, '')]
            ]))
            raise

    def endItem(self, lineData):
        """ to dispatch Protonabu Fact-block termination
            - Input: line Data
        """
        handler = self.handlers[lineData.label][1]
        # [Opt]: to dispatch protonabu fact end line parser
        if handler:
            # [Msg]: to [Using]: to handler
            handler(lineData)


class ProtonabuParser(SnippetParser):
    """ Protonabu Parser
        - Purpose: to parse Protonabu Fact from snippet tree
    """
    def __init__(self,
         schemaSourceAndTitle: ProtonabuSnippet | tuple[str, str] | ProtonabuSchema,
         homeFolder: Optional[Path] = None
    ):
        """ to INITIALIZE Protonabu Parser
            - Exported
            - Input: schema ready or source
            - Input [Opt "None"]: home Folder
        """
        # [Alt]: to set protonabu parser input from ready schema 
        if isinstance(schemaSourceAndTitle, ProtonabuSchema):
            schema = schemaSourceAndTitle
        # [Alt]: to set protonabu parser input from source 
        else:
            # [Alt]: to prepare to set protonabu parser input from snippet
            if isinstance(schemaSourceAndTitle, ProtonabuSnippet):
                schemaSnippet = schemaSourceAndTitle
            # [Alt]: to prepare to set protonabu parser input from string
            else:
                schemaSource, schemaTitle = schemaSourceAndTitle
                # [Msg]: to create Protonabu Snippet In Memory
                schemaSnippet = ProtonabuSnippetInMemory(
                    schemaSource.split('\n'),
                    schemaTitle
                )
            # [msg]: to INITIALIZE Protonabu Schema
            schema = ProtonabuSchema(schemaSnippet)
        # [msg]: to INITIALIZE Protonabu Tokenizer
        SnippetParser.__init__(self, schema)
        self.homeFolder: Path = homeFolder if homeFolder else Path()

    def compile(self,
        inp: ProtonabuSnippet | ProtonabuSnippet.ISource,
        progressBar: Optional[IProgressIndicator]=None
    ):
        """ to compile <Protonabu> Parser source
            - Exported
            - definitive [Project]
            - Input: input snippet or source
            - Input [Opt "None"]: progress bar
        """
        # [Opt]:  to INITIALIZE Dummy Progress Indicator
        if not progressBar:
            # [Msg]: to INITIALIZE dummy progress indicator
            progressBar = DummyProgressIndicator()
        # [Opt]: to set protonabu Parser home folder from snippet
        if not self.homeFolder:
            fileName = Path(inp.fileName if isinstance(inp, ProtonabuSnippet) else getattr(inp, 'fileName', ''))
            # [Opt]: to set protonabu Parser home folder to parent of snippet source
            if fileName and fileName.exists():
                self.homeFolder = fileName.parent
        # [Opt "not a snippet"]: to create Protonabu Snippet from snippet source
        if isinstance(inp, ProtonabuSnippet.ISource):
            # [Msg]: to INITIALIZE Protonabu Snippet
            inp = ProtonabuSnippet(inp, getattr(inp, 'fileName', '<source>'))
        # [Msg]: to compile <SUBSTITUTE Snippet> Parser source
        SnippetParser.compile(self, inp, progressBar)

    def makePathName(self, fileName: Path)-> Path:
        """ to make protonabu parser path name
            - Exported
            - Input: file Name
            - Output: result
        """
        # [Esc Done]: absolute path
        if fileName.is_absolute(): return fileName.resolve()
        # [Msg]: to prepend home folder to relative protonabu parser file path
        return (self.homeFolder / fileName).resolve()

    def parseImportingDirective(self,
        lineData: TokenizedFact,
        _: Optional[Iterator[RawFact]]
    ):
        """ to parse <SUBSTITUTE> Protonabu Parser import immediate directive
            - Input: line Data
            - Input: unused iterator
        """
        pass


class ImportingProtonabuParser(ProtonabuParser, ABC):
    """ Importing Protonabu Parser
        - Purpose: to parse Protonabu Fact from snippet tree with importing support
    """
    def __init__(self,
         schemaSourceAndTitle: ProtonabuSnippet | tuple[str, str] | ProtonabuSchema,
         homeFolder: Optional[Path] = None
    ):
        """ to INITIALIZE Importing Protonabu Parser
            - Exported
            - Input: schema ready or source
            - Input [Opt "None"]: home Folder
        """
        # [msg]: to INITIALIZE Protonabu Parser
        ProtonabuParser.__init__(self, schemaSourceAndTitle, homeFolder)
        self.expandedImports: list[Path] = []
        self.fileTypes = ['.nabu', '.facts'] # searched in this order
        self.immediateHandlers['IMPORTING'] = self.parseImportingDirective

    def parseImportingDirective(self,
        lineData: TokenizedFact,
        _: Optional[Iterator[RawFact]]
    ):
        """ to parse <Importing> Protonabu Parser import immediate directive
            - Exported
            - Input: line Data
            - Input: unused iterator
            - definitive [Part]
        """
        def findFile(pathName: Path)-> Optional[Path]:
            """ to find protonabu parser file by extensions
                - Input: path name
                - Output [Opt]: path name
            """
            # [Scan extensions]: to find protonabu parser file by extension
            for ext in self.fileTypes:
                # [Esc Done]: Found
                if pathName.with_suffix(ext).exists():
                    return pathName.with_suffix(ext)
            # [Esc Exhausted]: Not found
            return None

        # [Esc Error]: Missing file name to import
        if not (
            origPathName := unquote(lineData.rawFact.arg).strip()
        ):
            raise Error('Missing file name to import')
        # [Esc Error]: File to import not found
        if not (
            pathName := findFile(self.makePathName(Path(origPathName)))
        ):
            raise Error('File to import not found', [
                ("path", self.makePathName(Path(origPathName)))
            ])
        # [Esc]: Already imported 
        if pathName in self.expandedImports: return
        # [Esc Error]: No active input snippet
        if not self.inp:
            raise InternalError('Parser has no active input snippet for importing')
        # [Msg]: to insert child snippet
        # - Using: to create Protonabu Snippet from file
        self.inp.insert(
            ProtonabuSnippetFromFile(pathName, isImporting=True)
        )
        self.expandedImports.append(pathName)
        # [Msg]: to add import
        self.addImport(origPathName, lineData.rawFact.label, self.currentRank1[1])

    @abstractmethod
    def addImport(self, pathName: str, label: str, title: str): 
        """ to add import to <SUBSTITUTE Importing Protonabu> Parser
            - Input: path Name
            - Input: label
            - Input: title
        """
        pass
