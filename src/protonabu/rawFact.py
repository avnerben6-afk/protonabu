""" Module: Protonabu Raw Fact
    - Author: Avner Ben
        - Created: 1-Apr-2017
        - Improved: 23-Aug-2026
          - Prepared for release
    - Generator: Antigravity (Gemini 3.7 Flash)
        - Improved: 25-Aug-2026
"""

import re
from enum import Enum
from abc import ABC, abstractmethod
from typing import Iterable, Iterator, Any, Optional, Sequence, TypeVar, Generic

from .util.error import Error, InternalError


class EditDirective(Enum):
    """ Edit Directive
        - Purpose: Enumeration for fact edit directives
        - INCOMPLETE: Marks facts that need completion (persistence: '...')
        - OBSOLETE: Marks facts for deletion (persistence: '--')
        - FORCED: Marks facts that are forced/required (persistence: '!!')
    """
    INCOMPLETE = 'INCOMPLETE'
    OBSOLETE = 'OBSOLETE'
    FORCED = 'FORCED'

    @classmethod
    def fromSymbol(cls, symbol: str) -> 'EditDirective | None':
        """ to convert persistence symbol to enum value
            - Input: cls
            - Output: result
        """
        _symbol_map = {
            '...': cls.INCOMPLETE,
            '--': cls.OBSOLETE,
            '!!': cls.FORCED
        }
        return _symbol_map.get(symbol)

    def toSymbol(self) -> str:
        """ to convert enum value to persistence symbol
            - Output: result
        """
        return {
            EditDirective.INCOMPLETE: '...',
            EditDirective.OBSOLETE: '--',
            EditDirective.FORCED: '!!',
        }[self]

    def isIncomplete(self) -> bool:
        """ to check if directive is INCOMPLETE
            - Output: result
        """
        return self == EditDirective.INCOMPLETE

    def isObsolete(self) -> bool:
        """ to check if directive is OBSOLETE
            - Output: result
        """
        return self == EditDirective.OBSOLETE

    def isForced(self) -> bool:
        """ to check if directive is FORCED
            - Output: result
        """
        return self == EditDirective.FORCED


class LookaheadIterator(Iterator[str]):
    """ Lookahead Iterator
        - Purpose: Iterator caching the current element
    """
    def __init__(self, itr: Iterable[str]):
        """ to INITIALIZE Lookahead Iterator
            - Input: object to iterate in   
        """
        self.itr: Iterator[str] = iter(itr)
        self.none: str = 'none'
        self.nextElement: str = self.none
        self.lastElement: str = self.none

    def __next__(self) -> str:
        """ to consume next Lookahead Iterator element caching
            - Output: result
        """
        # [Esc Done]: "lookahead"
        if self.nextElement is not self.none:
            result: str = self.nextElement
            self.nextElement = self.lastElement = self.none
            return result
        # [Guard]: to EXTRACT next element from Lookeahead Iterator content
        try:
            self.lastElement = next(self.itr)
            return self.lastElement
        # [Esc Error]: End of iteration
        except StopIteration:
            raise

    def regret(self):
        """ to regret Lookahead Iterator progress
        """
        self.nextElement = self.lastElement

    def remember(self, c: str):
        """ to push Lookahead Iterator content
            - Input: c
        """
        self.nextElement = c


class RawFact:
    """ "Raw Fact"
        - Purpose: Raw textual representation of Labeled Fact
        - Contents: label, [0-N label modifier, [0-1 argument, 0-N argument modifier]]
    """
    tab: str = '    '
    tabSize = len(tab)
    maxW: int = 120
    maxWithArgW: int = 100

    labelPattern = re.compile(r'(!!|--|\s*)([a-zA-Z][a-zA-Z0-9 ]*|__[a-zA-Z][a-zA-Z0-9_]*__)')
    bracketedItemTokenPattern = re.compile(r'".*?"|(?<!\w)\'.*?\'(?!\w)|;|\]|([^"\';\]]|(?<=\w)\'|\'(?=\w))+')
    argPattern = re.compile(r'".*?"|(?<!\w)\'.*?\'(?!\w)|\[\]=?|\[|([^"\'\[]|(?<=\w)\'|\'(?=\w))+')
    editDirectivePattern = re.compile(r" (\.\.\.|--|!!)$")
    trailingCommentPattern = re.compile(r'(\"[^\"]*\")|\s//')

    def __init__(self,
        label: Optional[str] = None,
        labelModifiers: Optional[str | Iterable[str]] = None,
        arg: Optional[str] = None,
        argModifiers: Optional[str | Iterable[str]] = None,
        editDirective: Optional[EditDirective] = None
    ):
        """ to INITIALIZE Raw Fact
            - Exported
            - Input: label
            - Input [Opt]: label modifiers
            - Input [Opt]: argument
            - Input [Opt]: argument modifiers
            - Input [Opt]: edit directive
        """
        self.label: str = label if label else ''
        self.rawLabel: str = label if label else ''
        self.labelModifiers: list[str] = []
        # [Opt]: to set label modifiers in Raw Fact
        if labelModifiers:
            # [Alt "string"]: to set single label modifier in Raw Fact
            if isinstance(labelModifiers, str):
                self.labelModifiers.append(labelModifiers)
            # [Alt "list"]: to set multiple label modifiers in Raw Fact
            else:
                self.labelModifiers += labelModifiers
        self.arg: str = arg if arg else ''
        self.argModifiers: list[str] = []
        # [Opt]: to set argument modifiers in Raw Fact
        if arg and argModifiers:
            # [Alt "string"]: to set single argument modifier in Raw Fact
            if isinstance(argModifiers, str):
                self.argModifiers.append(argModifiers)
            # [Alt "list"]: to set multiple argument modifiers in Raw Fact
            else:
                self.argModifiers += argModifiers
        self.comment: str = ''
        self.rank: int = 0
        self.fileName: str = ''
        self.lineNumber: int = 0
        self.isImporting: bool = False  # deprecated
        self.editDirective: Optional[EditDirective] = editDirective

    def reset(self):
        """ to reset Raw Fact before parsing
        """
        self.label = ''
        self.rawLabel = ''
        self.labelModifiers = []
        self.arg = ''
        self.argModifiers = []
        self.comment = ''
        self.rank = 0
        self.isImporting = False
        self.editDirective = None

    def isEmpty(self) -> bool:
        """ to tell if Raw Fact is empty
            - Output: Empty indication
        """
        return not self.label and not self.comment

    def toCompositeFact(self, isFirst: bool = False) -> list[str]:
        """ to restore Labeled Fact to one or more Fact lines
            - Exported
            - definitive 
            - Input: is First indicator
            - Output: List of fact lines
        """
        def add(s: str, isNewLine=False):
            """ to accumulate restored fact printout breaking long lines
                - Input: String to add
                - Input: New line before indicator
            """
            # [Msg]: to detect commented fact line
            isComment = s.startswith('// ')
            # [Rpt]: to cut fact line
            while s:
                # [Opt]: to begin continuation line
                if isNewLine:
                    lines.append(leadIn + ('// ' if isComment else '- '))
                # [opt]: to separate next token with space
                if lines[-1] and not lines[-1][-1].isspace() and not s.startswith(':'):
                    lines[-1] += ' '
                # [Esc Done]: len lines 1 len s rest
                if (len(lines[-1]) + len(s) >= self.maxW):
                    # [Esc]: indent exceeds max width
                    if len(leadIn) > self.maxW:
                        # to glue fact-line content to the last line
                        lines[-1] += s
                        break
                    # [Msg]: to find convenient breaking point
                    posBreak = s.rfind(' ', 0, self.maxW - len(lines[-1]) + 1)
                    # [Esc]: Nowhere to break
                    if posBreak == -1:
                        # [Msg]: to open new restored fact line
                        lines.append(leadIn + ('// ' if isComment else '- '))
                        lines[-1] += s
                        break
                    # to cut the next token at last blank
                    lines[-1] += s[:posBreak]
                    s = s[posBreak:].lstrip()
                    # [Msg]: to open new restored fact line
                    lines.append(leadIn + ('// ' if isComment else '- '))
                # [Esc Exhausted]: last portion
                else:
                    # to glue fact-line content to the last line
                    lines[-1] += s
                    break

        # to indent restored raw fact
        leadIn = self.tab * (self.rank - 1)
        lines: list[str] = [leadIn]
        # [opt]: to restore raw fact proper
        if self.label:
            # [Msg]: to accumulate restored fact printout breaking long lines
            add(self.label)
            # [opt]: to accumulate restored fact printout breaking long lines
            if self.labelModifiers:
                modifiers = '; '.join(self.labelModifiers)
                # [Msg]: to accumulate restored fact printout breaking long lines
                add(f'[{modifiers}]')
            # [opt]: to restore raw fact argument and modifiers
            if self.arg:
                # [Msg]: to accumulate restored fact printout breaking long lines
                add(f': {self.arg}')
                # [opt]: to accumulate restored fact printout breaking long lines
                if self.argModifiers:
                    modifiers = f"[{'; '.join(self.argModifiers)}]"
                    # [Msg]: to accumulate restored fact printout breaking long lines
                    add(
                        modifiers,
                        isNewLine=bool(lines[-1].strip() and len(lines[-1]) + len(modifiers) + 1 >= self.maxWithArgW)
                    )
            # [opt]: to restore raw fact edit directive
            if self.editDirective:
                # [Msg]: to accumulate restored fact printout breaking long lines
                add(self.editDirective.toSymbol())
        # [opt]: to restore raw fact comment line
        if self.comment:
            # [Msg]: to accumulate restored fact printout breaking long lines
            add(f'// {self.comment}')
        return lines

    def fromCompositeFact(self,
        inSource: LookaheadIterator | Iterable[str] | str,
        pendingRankIndents: Optional[list[int]] = None,
        isFirst: bool = False
    ) -> tuple[int, int]:
        """ to parse one Labeled Fact raw elements from Fact stream
            - definitive [Part]
            - Input: fact line or block to read
            - Input: indent history
            - Output: parsing state
            - Contains: number of lines read
            - Contains: raw indent
            - Input [Opt "False"]: is First
        """
        def parseLabel(s: str) -> str:
            """ to parse Fact label
                - Input: Fact Line
                - Output [State]: Raw Fact label
                - Output: Fact Line -- minus label
            """
            matched = self.labelPattern.match(s)
            # [Esc]: no label
            if not matched:
                raise Error('Missing label in fact', [('GIVEN', s)])
            self.rawLabel = matched.group(2).rstrip()
            self.label = self.rawLabel.upper()
            return s[matched.end():].lstrip()

        def parseModifiers(s: str, modifiers: list[str]) -> str:
            """ to parse Fact bracketed modifiers
                - Input: Fact Line -- at start bracket
                - Output [State]: Raw Fact modifiers
                - Output: Fact Line -- minus modifiers
            """
            modifier = ''
            s = s[1:].lstrip()
            # [Rpt Untill end bracet]: to parse raw modifier
            while not s.startswith(']'):
                matched = self.bracketedItemTokenPattern.match(s)
                # [Esc Done]: not a modifier
                if not matched: break
                s = s[matched.end():].lstrip()
                modifier = (' '.join((modifier, matched.group().strip()))).lstrip()
                # [Esc]: startswith of s
                if s.startswith((';', ']')):
                    # [Esc Error]: "Empty modifier"
                    if not modifier:
                        raise Error('Missing fact argument')
                    modifiers.append(modifier)
                    modifier = ''
                    # [Opt]: to skip modifier separator
                    if s.startswith(';'):
                        s = s[1:].lstrip()
            # [Esc Error]: "Non-terminated label modifier"
            if not modifiers and not s.startswith(']'):
                raise Error('Non-terminated label modifier. Expected closing bracket')
            s = s[1:].lstrip()
            return s

        def parseArgument(s: str) -> str:
            """ to parse fact argument
                - Input: Fact Line -- at argument start
                - Output [State]: Raw Fact argument
                - Output: Fact Line -- minus argument
            """
            # [Esc]: not s rstrip
            if not s.rstrip(): return ''
            # to separate trailing comment from raw fact argument outside double quotes
            pos = 0
            # [Scan]: to find unquoted comment delimiter
            while match := self.trailingCommentPattern.search(s, pos):
                # [Alt "double-quoted string"]: to skip quoted token
                if match.group(1):
                    pos = match.end()
                # [Alt "unquoted comment"]: to split trailing comment
                else:
                    comment = s[match.end():].strip()
                    s = s[:match.start()]
                    # to prepend new comment to existing comment
                    self.comment = f'{comment} {self.comment}' if self.comment else comment
                    break
            # [Scan]: to build raw fact argument
            while s and not s.startswith('//'):
                # [Esc]: arg modifier excluding the subscript operator
                if s.startswith('[') and not s.startswith('[]'): break
                matched = self.argPattern.match(s)
                # [Esc]: not an arg token
                if not matched:
                    # [Esc]: Non-terminated fact argument
                    if not self.arg:
                        raise Error('Non-terminated fact argument', [('Label', self.label), ('Argument', s)])
                    break
                arg = matched.group().strip()
                # [Opt]: to join argument tokens
                if self.arg and not arg.startswith('['):
                    self.arg += ' '
                self.arg += arg
                s = s[matched.end():].lstrip()
            return s

        def prepareLine(s: str) -> tuple[str, int]:
            """ to prepare raw fact line for processing
                - Input: raw fact line
                - Output: Parsing state
                - Contains: Raw fact line -- stripped
                - Contains: Indent
            """
            # [Msg]: to strip trailing blanks from raw fact line
            s = s.rstrip()
            # [Msg]: to expand raw fact line tabs to spaces
            s1 = s.expandtabs(self.tabSize)
            # [Msg]: to strip leading blanks and calculate raw fact line indent
            s = s.lstrip()
            return s, len(s1) - len(s)

        def joinContinuationLines(baseLine, count) -> tuple[str, int]:
            """ to join raw Fact continuation lines and collect comments
                - Input: Raw Fact Line
                - Input: Line count
                - Output: Parsing state
                - Contains: Raw fact line -- ?
                - Contains: Indent
            """
            isComment = False
            # [Guard]: to join continuation lines
            try:
                # [scan rest of lines]: to join continuation line
                while True:
                    # [Msg]: to peek next raw fact line
                    nextLine = next(source).rstrip()
                    # [Esc]: blank line
                    if not nextLine:
                        # [Msg]: to force read next blank line
                        source.remember('')
                        break
                    # [Msg]: to prepare raw fact line for processing
                    nextLine, nextIndent = prepareLine(nextLine)
                    # [Esc Done]: is Comment
                    if isComment:
                        # [Esc Done]: not lstrip of next Line rest
                        if not nextLine.lstrip().startswith('//'):
                            # [Msg]: to regret Lookahead Iterator progress
                            source.regret()
                            break
                    # [Esc Once]: comment line
                    # to remember pending comment part temporarily
                    if nextLine.lstrip().startswith('//'):
                        # [Opt]: to space comment before continuation
                        if self.comment:
                            self.comment += ' '
                        self.comment += nextLine[2:].lstrip()
                        count += 1
                        isComment = True
                        continue
                    # [Esc]: not a continuation line
                    if nextIndent != indent or not nextLine.startswith('- '):
                        # [Msg]: to regret Lookahead Iterator progress
                        source.regret()
                        break
                    # to join continuation line to raw fact
                    baseLine += nextLine[1:]
                    count += 1
            # [Esc Ignored]: StopIteration
            except StopIteration:
                pass
            return baseLine, count

        def convertSource(src: LookaheadIterator | Iterable[str] | str)-> LookaheadIterator:
            """ to convert raw-fact source to Lookahead Iterator
            """
            # [Esc Done]: "Nothing to convert"
            if isinstance(src, LookaheadIterator): return src
            # [Opt]: to convert raw-fact string source to iterable
            if isinstance(src, str):
                src = (src,)
            # [Guard]: to INITIALIZE Lookahead Iterator
            try:
                # [Msg]: to INITIALIZE lookahead iterator
                return LookaheadIterator(iter(src))
            # [Esc Error]: "source is not iterable"
            except TypeError:
                raise InternalError('non-iterable source for raw fact')

        def computeRank():
            """ to compute raw fact rank
            """
            # [Esc]: "Pending ranks unset"
            if pendingRankIndents is None: return
            # [Alt "no pending ranks given"]: to set raw fact rank to one
            if not pendingRankIndents:
                self.rank = 1
            # [Alt "indent greater than last"]: to set raw fact rank to next rank
            elif indent > pendingRankIndents[-1]:
                self.rank = len(pendingRankIndents) + 1
            # [Alt "indent less than or equal to last"]: to set raw fact rank to corresponding rank
            else:
                # [Guard]: to resolve existing rank index
                try:
                    self.rank = pendingRankIndents.index(indent) + 1
                # [Esc error]: invalid indent
                except ValueError:
                    raise Error('Invalid indent', [
                        ('Indent', indent),
                        ('Expected', ', '.join([str(x) for x in reversed(pendingRankIndents)])),
                        ('Text', line)
                    ])

        # [Msg]: to reset Raw Fact before parsing
        self.reset()
        # [Msg]: to convert raw-fact source to Lookahead Iterator
        source: LookaheadIterator = convertSource(inSource)    
        # [Guard]: to obtain raw fact line
        try:
            # to consume next Lookahead Iterator element caching
            line, numLinesRead = next(source), 1
            # [opt]: to get rid of Unicode BOM at Fact start
            if isFirst and line.startswith((u'\ufeff', '\x00')):
                line = line[1:]
            # [Msg]: to get rid of trailing newline in Fact line
            line = line.rstrip()
        # [Esc]: blank block
        except StopIteration:
            return 0, 0
        # [Guard]: to parse one labeled fact raw elements from fact stream
        try:
            # [Scan lines]: to consume next Lookahead Iterator element caching
            # - Giving: Raw fact line and indent
            # - Giving: Number of raw fact lines consumed
            while not line.strip() or line.lstrip().startswith('//'):
                line, numLinesRead = next(source), numLinesRead + 1
        # [Esc]: blank block
        except StopIteration:
            return numLinesRead, 0
        # [Msg]: to prepare raw fact line for processing
        line, indent = prepareLine(line)
        # [Msg]: to join raw Fact continuation lines and collect comments
        line, numLinesRead = joinContinuationLines(line, numLinesRead)
        # ...to obtain raw fact line

        # [Msg]: to compute raw fact rank
        computeRank()

        # to tokenize raw fact...
        # [Opt "Leftover trailing edit directive"]: to parse trailing edit directive
        if (match := self.editDirectivePattern.search(line)):
            # [Msg]: to convert persistence symbol to enum value
            self.editDirective = EditDirective.fromSymbol(match.group(1))
            line = line[:match.start()].rstrip()
        # [Msg]: to parse fact label
        line = parseLabel(line)
        # [Esc]: "label-only fact"
        if not line: return numLinesRead, indent
        # [opt]: to parse Fact bracketed modifiers
        # - giving: raw label modifiers
        if line.startswith('['):
            # [Msg]: to parse Fact bracketed modifiers
            line = parseModifiers(line, self.labelModifiers)
        # [Alt "Colon"]: to proceed parsing line after label and colon
        if line.startswith(':'):
            line = line[1:].lstrip()
        # [Alt "no colon"]: to consider comment line
        elif line:
            # [Esc]: Comment line
            if line.startswith('//'):
                self.comment = line[2:].lstrip()
                # [Esc]: line.startswith('//')
                return numLinesRead, indent
        # [Msg]: to parse fact argument
        line = parseArgument(line)
        # [opt]: to parse Fact bracketed modifiers
        # - giving: raw label modifiers
        if self.arg and line.startswith('['):
            # [Msg]: to parse Fact bracketed modifiers
            line = parseModifiers(line, self.argModifiers)
        # [Opt "Edit directive after argument"]: to parse trainling edit directive
        if (
            self.arg and not self.editDirective
            and (match := self.editDirectivePattern.search(self.arg))
        ):
            self.editDirective = EditDirective.fromSymbol(match.group(1))
            self.arg = self.arg[:match.start()].rstrip()
        # ...to tokenize raw fact

        # [Alt "Comment symbol"]: to parse trailing raw fact comment
        if (line := line.lstrip()).startswith('//'):
            line = line[2:].lstrip()
            # [Alt]: to prepend line to comment
            self.comment = f'{line} {self.comment}' if self.comment else line
        # [Esc Exhausted]: "Excess information in fact"
        elif line:
            quote = "'" if line.startswith('"') else '"'
            # [Esc]: 
            raise Error(f'Excess information in fact: {quote}{line}{quote}')
        # to return lines read and indent
        return numLinesRead, indent

    def setLabel(self, label: str):
        """ to set label in Raw Fact
            - Input: "Label"
        """
        self.label = label

    def addLabelModifier(self, modifier: str):
        """ to add label modifier to Raw Fact
            - Input: "Label modifier"
        """
        self.labelModifiers.append(modifier)

    def setArgument(self, arg: str):
        """ to set argument in Raw Fact
            - Input: "Argument"
        """
        self.arg = arg

    def addArgModifier(self, modifier: str):
        """ to add label modifier to Raw Fact
            - Input: "Argument modifier"
        """
        self.argModifiers.append(modifier)

    def setComment(self, comment: str):
        """ to set comment in Raw Fact
            - Input: "Comment"
        """
        self.comment = comment

    def setRank(self, rank: int):
        """ to set comment in Raw Fact
            - Input: "rank"
        """
        self.rank = rank


T = TypeVar('T', bound='ProtonabuParsingStack.Stackable')
class ProtonabuParsingStack(Generic[T]):
    """ Protonabu Parsing Stack
        - Purpose: to track nested Labeled Fact
    """
    class Stackable(ABC):
        """ Stackable
            - Purpose: placeHolder for objects that can be added to the parsing stack
        """
        label: Any = None

        @abstractmethod
        def getChildren(self) -> Sequence[ProtonabuParsingStack.Stackable]:
            """ to get children of Stackable <SUBSTITUTE>
                - Output: list of Stackable objects
            """
            ...

    def __init__(self):
        """ to INITIALIZE rank stack
        """
        self.ranks: list[tuple[str, T]] = []
        self.saved: list[list[tuple[str, T]]] = []

    def update(self,
        rank: int,
        label: str,
        obj: T
    ):
        """ to update the rank stack
            - Input: rank
            - Input: label
            - Input: obj
        """
        # [Rpt]: to pop rank levels
        while len(self.ranks) > rank:
            self.ranks.pop()
        # Error: wrong rank level exposed
        # [Esc]: rank is not len self ranks
        if rank != len(self.ranks):
            raise InternalError(f'Invalid Parsing stack rank', [('Label', label), ('Rank', rank)])
        # [Msg]: to append rank level
        self.ranks.append((label, obj))

    def endBlock(self, rank, label: str):
        """ to match explicit <SUBSTITUTE Protonabu> Parsing Stack block ending with or without label
            - Input: rank
            - Input: label
        """
        # [Scan]: to pop rank level
        while len(self.ranks) > rank + 1:
            self.ranks.pop()
        # [Esc]: label
        if label:
            # [Esc Error]: "Closed block not opened above"
            if self.ranks[-1][0] != label:
                raise Error(f'Closed block not opened above', [
                    ('Label', label), 
                    ('Actual', self.ranks[-1][0])
                ])
            # [Msg]: to get children of Stackable <SUBSTITUTE>
            children = self.ranks[-2][-1].getChildren()
            # [Esc Error]: "Closed block not opened above"
            if not any(x.label and x.label.name == label for x in children):
                raise Error('Closed block not opened above', [('Label', label)])
        # [Esc Error]: "Invalid parsing stack rank at block-end"
        if rank != len(self.ranks) - 1:
            raise InternalError(f'Invalid parsing stack rank at block-end', [('Specified', label)])
        self.ranks.pop()

    def getParent(self) -> Optional[T]:
        """ to get parent of current indented object
            - definitive [Part]
            - Output: result
        """
        i = -2
        # [Guard]: to get parent of current indented object
        try:
            # [Rpt]: to pop from rank history
            while not self.ranks[i][1]:
                i -= 1
            return self.ranks[i][1]
        # [Esc Error]: "IndexError"
        except IndexError:
            return None

    def pop(self):
        """ to pop level from the rank stack
        """
        # [Esc Error]: "Parsing stack emptied"
        if len(self.ranks) == 1:
            raise InternalError('Parsing stack emptied')
        self.ranks.pop()

    def getRank(self) -> int:
        """ to tell current rank level
            - Output: result
        """
        return len(self.ranks) - 1
    
    def save(self):
        """ to save the current parsing stack
        """
        self.saved.append([(x[0], x[1]) for x in self.ranks])

    def restore(self):
        """ to restore the current parsing stack
        """
        # [Esc Error]: "Cannot restore the parsing stack"
        if not self.saved:
            raise InternalError('Cannot restore the parsing stack')
        self.ranks = self.saved.pop()
