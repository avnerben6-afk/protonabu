""" Module: Protonabu Snippet Module
    - Author: Avner Ben
        - Created: 1-Jan-2020
        - Revised: 24-Jun-2026
            - Separated from fact SnippetParser
        - Improved: 26-Aug-2026
            - Prepared for release
"""

from pathlib import Path
from abc import ABC, abstractmethod
from typing import Any, Iterable, Iterator, Optional, Callable, TextIO

from .util.error import Error, InternalError, FactFileError
# [Additional]
from .rawFact import RawFact, LookaheadIterator


class ProtonabuSnippet:
    """ Protonabu Snippet
        - Purpose: to parse Protonabu Fact from snippet
    """
    class ISource(ABC):
        """ Fact Stream
        """
        @abstractmethod
        def add(self, fact: str):
            """ to append line to <SUBSTITUTE> Fact Stream
                Input: line
            """
            pass

        @abstractmethod
        def __iter__(self) -> Iterator[str]:
            """ to TRAVERSE <SUBSTITUTE> Fact Stream
                - definitive [Part]
                - Output: Fact line iterator
            """
            pass

        def close(self):
            """ to close <SUBSTITUTE> Fact Stream
            """
            pass # nothing to doby default


    def __init__(self,
        source: ISource,
        fileName: str,
        isImporting: bool = False # deprecated
    ):
        """ to INITIALIZE Protonabu Snippet
            - Exported
            - Input: Fact Stream
            - Input: File name
            - Input: Is importing indication
        """
        self.fileName = fileName
        self.name = fileName
        # [Esc Error]: Invalid snippet source type
        if not isinstance(source, ProtonabuSnippet.ISource):
            raise InternalError('Invalid snippet source')
        # Contains [1:1 By Value]: Fact Stream
        self.source: ProtonabuSnippet.ISource = source
        self.isImporting: bool = isImporting # deprecated
        # Contains [1:0-N by Value] Protonabu Snippet [role "child"] 
        # - Key: "triggering rank"
        # - Use: Child snippets are consumed when rank falls below this rank. 
        #        Child snippets ranked zero are inserted at start
        self.children: dict[int, list[ProtonabuSnippet]] = {}
        # Containes [0-1:1 By Reference] Protonabu Snippet [role "current in children"]
        self.currentChild: ProtonabuSnippet = self
        self.lineNum = 0
        self.parsingStack: Optional[Any] = None

    def __iter__(self) -> Iterator[RawFact]:
        """ to TRAVERSE Protonabu Snippet <SUBSTITUTE>
            - Definitive [Part]
            - Output: Raw Fact iterator
        """
        def processLine()-> RawFact:
            """ to parse next labeled fact in Protonabu Snippet
                - Output [Opt empty]: current Raw Fact
            """
            # [Msg]: to INITIALIZE Raw Fact
            rawFact = RawFact()
            # [Guard]: to parse Raw Fact from Fact stream
            try:
                innerLineCount, indent = rawFact.fromCompositeFact(itr, ranks)
            # [Esc Error]: Parsing error
            except Error as err:
                err.set('Filename', f'{self.fileName}:{self.lineNum}')
                raise
            # [Esc]: blank line at EOF
            if not innerLineCount or not rawFact.label:
                raise StopIteration
            # [Alt]: to stack pending snippet rank
            if rawFact.rank > len(ranks):
                ranks.append(indent)
            # [Alt]: to pop expired rank from snippet
            else:
                # [Rpt "While expired"]: to pop expired rank from snippet
                while len(ranks) > rawFact.rank:
                    ranks.pop()
            self.lineNum += innerLineCount
            rawFact.lineNumber = self.lineNum
            return rawFact

        def iterRank(rank: int) -> Iterator[ProtonabuSnippet]:
            """ to TRAVERSE Protonabu Snippet rank
                - Output: Sibling snippet iterator
            """ 
            # [Esc]: no such rank
            if rank not in self.children: return
            # [Rpt "While rank"]: to prepare to expand child Snippet
            while rank in self.children and self.children[rank]:
                self.currentChild = self.children[rank][0]
                # to forget child snippet
                self.children[rank].pop(0)
                # [Opt]: to forget pending snippet rank
                if not self.children[rank]:
                    self.children.pop(rank)
                yield self.currentChild
                self.currentChild = self

        def iterChildren(currentRank) -> Iterator[ProtonabuSnippet]:
            """ to TRAVERSE pending child snippets
                - Output: child snippet iterator
            """
            # [Scan]: to prepare to expand child Snippets in pending rank
            for rank in sorted(self.children.keys()):
                # [Esc]: child snippet rank not due yet
                if rank < currentRank: continue
                # [Scan to TRAVERSE snippet rank]: to prepare to expand child Snippet
                yield from iterRank(rank)
            return

        self.lineNum = 0
        ranks: list[int] = []
        # [Msg]: to INITIALIZE Lookahead Iterator
        itr = LookaheadIterator(self.source)
        # [Rpt "While snippet"]: to read next valid line from snippet source
        while True: 
            # [Guard]: to do read next valid line from snippet source
            try:
                # [Msg]: to parse next labeled fact in Snippet
                fact = processLine()
                # to update Raw Fact file name
                fact.fileName = self.fileName
                # to update Raw Fact importing status
                fact.isImporting = self.isImporting 
                # [Opt]: to save the parsing stack
                if self.parsingStack:
                    self.parsingStack.save()
                # [Scan]: to TRAVERSE pending child snippets
                for pendingExpand in iterChildren(fact.rank):
                    yield from pendingExpand
                # [Opt]: to restore the parsing stack
                if self.parsingStack:
                    self.parsingStack.restore()
                yield fact
            # [Esc Done]: "End of iteration"
            except StopIteration:
                break
            # [Esc Error]: "Parsing error"
            except FactFileError:
                raise
        self.currentChild = self
        # [Scan]: to TRAVERSE pending child snippets
        for pendingExpand in iterChildren(0):
            yield from pendingExpand
        # [Msg]: to close Snippet source
        self.source.close()

    def add(self, fact: Optional[RawFact | str]) -> int:
        """ to add fact to Protonabu Snippet <SUBSTITUTE>
            - Input [Opt]: Raw Fact
            - Output: Number of lines added
        """
        # [Esc]: Blank line
        if not fact:
            # [Msg]: to append line to <SUBSTITUTE> Fact Stream 
            # - Using: blank
            self.source.add('')
            return 1
        # [Esc]: Litteral line controlling fact editing behavior
        if isinstance(fact, str):
            # [Msg]: to append line to <SUBSTITUTE> Fact Stream
            # - Using: line
            self.source.add(fact)
            return 1
        # [Scan]: to print raw Protonabu Fact line
        for line in (
            # [Msg]: to restore Labeled Fact to one or more Fact lines
            lines:= fact.toCompositeFact()
        ):
            # [Msg]: to append line to <SUBSTITUTE> Fact Stream
            # - Using: line
            self.source.add(line)
        return len(lines)

    def close(self):
        """ to close Protonabu Snippet <SUBSTITUTE>
        """
        # [Msg]: to close <SUBSTITUTE> Fact Stream
        # = From: main snippet source
        self.source.close()
        # [Msg; Scan pending snippet rank; Scan children]: to close Protonabu Snippet
        for children in self.children.values():
            for child in children:
                child.close()

    def insert(self, snippet: "ProtonabuSnippet", rank: int = 1):
        """ to insert child snippet
            - Input: snippet
            - Input [Opt 1]: rank
        """
        # [Esc]: nested import
        if self.currentChild is not self:
            # [Msg]: to insert child snippet
            self.currentChild.insert(snippet, rank)
            return
        # [Opt]: to schedule child snippet after current Protonabu Fact 
        if rank not in self.children:
            self.children[rank] = []
        self.children[rank].append(snippet)


class ProtonabuMemorySource(ProtonabuSnippet.ISource):
    """ In Memory Fact Stream
    """
    def __init__(self, source: Optional[Iterable[str]]=None):
        """ to INITIALIZE Protonabu Snippet source In Memory
            - Exported
            - Input [Opt]: Source lines
        """
        self.source: Iterable[str] = source if source else []

    def add(self, fact: str):
        """ to append line to <In Memory> Fact Stream
            - Input: line to append
        """
        # [Opt]: to convert source to list
        if not isinstance(self.source, list):
            self.source = list(self.source)
        # [Alt]: to add Fact lines to memory snippet source
        # - Using: to restore Labeled Fact to one or more Fact lines
        if isinstance(fact, RawFact):
            self.source.extend(fact.toCompositeFact())
        # [Alt]: to add fact line to memory snippet source
        else:
            self.source.append(fact)

    def __iter__(self) -> Iterator[str]:
        """ to TRAVERSE <In Memory> Fact Stream
            - definitive [Part]
            - Output: Fact line iterator
        """
        return iter(self.source)


def ProtonabuSnippetInMemory(
    source: Iterable[str],
    fileName: str
) -> ProtonabuSnippet:
    """ to create Protonabu Snippet In Memory
        - Exported
        - Input: fact source
        - Input: file name
        - Output: Protonabu Snippet
    """
    # [Msg]: to INITIALIZE Protonabu Snippet
    # - Using: to INITIALIZE Protonabu Snippet source In Memory
    return ProtonabuSnippet(
        ProtonabuMemorySource(source),
        fileName
    )


class ProtonabuToOpenFileSource(ProtonabuSnippet.ISource):
    """ Into Open File Fact Stream 
    """
    def __init__(self,
        outp: TextIO,
        toCloseSource: Optional[Callable[[], None]] = None
    ):
        """ to INITIALIZE Into Open File Fact Stream
            - Input: output file stream
            - Input [Opt]: to close source
        """
        self.outp: TextIO = outp
        self.toCloseSource: Callable[[], None] = (
            toCloseSource if toCloseSource 
            else lambda: None
        )

    def add(self, fact: str):
        """ to append line to <Into Open File> Fact Stream
            - Input: fact to append
        """
        self.outp.write(fact + '\n')

    def __iter__(self) -> Iterator[str]:
        """ to TRAVERSE <Into Open File> Fact Stream
            - definitive [Part]
            - Output: Dummy fact line iterator
        """
        return iter([])

    def close(self):
        """ to close <Into Open File> Fact Stream
        """
        # [Msg]: to close source
        self.toCloseSource()


def ProtonabuSnippetToOpenFile(
    outp: TextIO,
    fileName: str,
    toCloseSource: Optional[Callable[[], None]] = None
) -> ProtonabuSnippet:
    """ to create Protonabu Snippet streaming to open file
        - Input: "output file stream"
        - Input: file name
        - Input [Opt]: "to close source"
    """
    # [Msg]: to INITIALIZE Protonabu Snippet
    # - Using: to INITIALIZE Into Open File Fact Stream
    return ProtonabuSnippet(
        ProtonabuToOpenFileSource(outp, toCloseSource),
        fileName
    )


class ProtonabuToFileSource(ProtonabuToOpenFileSource):
    """ Into file Fact Stream
    """
    def __init__(self,
        pathName: Path,
        isFirst: bool = False
    ):
        """ to INITIALIZE Protonabu Snippet source to file
            - Input: path name
            - Input [Opt False]: is First
        """
        # [Esc Error]: folder not found
        if not pathName.parent.exists():
            raise Error('Path not found', [('Path', str(pathName.parent))])
        # [Guard]: to open snippet source file
        try:
            outp: TextIO = open(pathName, 'w', encoding='utf-8')
        # [Esc Error]: cannot open file
        except Exception as error:
            raise Error('cannot open file', [('Path', str(pathName)), ('Reason', str(error))])
        # [Msg]: to INITIALIZE Into Open File Fact Stream
        ProtonabuToOpenFileSource.__init__(self, outp, outp.close)


def ProtonabuSnippetToFile(
    pathName: Path,
    fileName: str
) -> ProtonabuSnippet:
    """ to create Protonabu Snippet source to file
        - Exported
        - Input: path name
        - Input: file name
        - Output: Protonabu Snippet
    """
    # [Msg]: to INITIALIZE Protonabu Snippet
    # - Using: to INITIALIZE Protonabu Snippet source to file
    return ProtonabuSnippet(
        ProtonabuToFileSource(pathName),
        fileName
    )


class ProtonabuSnippetFromOpenFileSource(ProtonabuSnippet.ISource):
    """ from open file Fact Stream
    """
    def __init__(self,
        inp: TextIO,
        toCloseSource: Optional[Callable[[], None]] = None
    ):
        """ to INITIALIZE Protonabu Snippet source from open file
            - Input: input file stream
            - Input [Opt]: to close source
        """
        self.inp: TextIO = inp
        self.toCloseSource: Callable[[], None] = (
            toCloseSource if toCloseSource 
            else lambda: None
        )

    def add(self, fact: str):
        """ to append line to <from open file> Fact Stream
            - Input: fact to append
        """
        # [Esc Error]: "Writing to input Snippet"
        raise InternalError('Writing to input Snippet')

    def __iter__(self) -> Iterator[str]:
        """ to TRAVERSE <from open file> Fact Stream
            - definitive [Part]
            - Output: Fact line iterator
        """
        return iter(self.inp)

    def close(self):
        """ to close <from open file> Fact Stream
        """
        # [Msg]: to close source
        self.toCloseSource()


def ProtonabuSnippetFromOpenFile(
    inp: TextIO,
    toCloseSource: Optional[Callable[[], None]] = None
) -> ProtonabuSnippet:
    """ to create Protonabu Snippet from open file
        - Input: input file stream
        - Input [Opt]: to close source
        - Output: Protonabu Snippet
    """
    # [Msg]: to INITIALIZE Protonabu Snippet
    # - Using: to INITIALIZE Protonabu Snippet source from open file
    return ProtonabuSnippet(
        ProtonabuSnippetFromOpenFileSource(inp, toCloseSource),
        inp.name if hasattr(inp, 'name') else '<unknown>'
    )


class ProtonabuSnippetFromFileSource(ProtonabuSnippetFromOpenFileSource):
    """ from file Fact Stream
    """

    def __init__(self, pathName: Path):
        """ to INITIALIZE Protonabu Snippet source from file
            - Input: path name
            - Input [Opt False]: is First
        """
        # [Esc Error]: file not found
        if not pathName.exists():
            raise Error('File not found', [('Path', str(pathName))])
        # [Guard]: to open snippet file
        try:
            inp: TextIO = open(pathName, 'r', encoding='utf-8')
        # [Esc Error]: cannot open file
        except Exception as error:
            raise Error('cannot open file', [('Path', str(pathName)), ('Reason', str(error))])
        # [Msg]: to INITIALIZE Protonabu Snippet source from open file
        ProtonabuSnippetFromOpenFileSource.__init__(self, inp, inp.close)


from .adapter.adapterFactory import snippetAdapterFactory


def ProtonabuSnippetFromFile(
    pathName: Path,
    isImporting: bool=False
) -> ProtonabuSnippet:
    """ to create Protonabu Snippet from file
        - Exported
        - Input: path name
        - Input [Opt False]: is importing
        - Output: Protonabu Snippet
    """
    # [Msg]: to INITIALIZE Protonabu Snippet
    # - Using: to INITIALIZE Protonabu Snippet source from file
    snippet = ProtonabuSnippet(
        ProtonabuSnippetFromFileSource(pathName),
        str(pathName),
        isImporting
    )
    # [Opt]: to adapt snippet input using registered Adapter
    if snippetAdapterFactory.hasAdapter(str(pathName)):
        # [Msg]: to adapt snippet input using registered Adapter
        snippet = snippetAdapterFactory.adaptInput(snippet)
    return snippet
    
