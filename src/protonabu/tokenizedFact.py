""" Module: Tokenized Fact Module
    - Purpose: Fact Tokenizer used and exported by protonabu Parser
    - Author: Avner Ben
        - Created: 1-Apr-2017
        - Revised: 24-Jul-2026
        - Improved: 23-Aug-2026
          - Prepared for release
    - Generator: Antigravity (Gemini 3.6 Flash)
        - Improved: 24-Jul-2026
"""

from collections.abc import Iterable
from pathlib import Path
import re
from typing import Any, Optional, Iterator

from .util.error import Error
from .util.stringUtil import cleanEnd
# [Additional]
from .rawFact import RawFact
# [Additional]
from .primitiveTokens import endToken, quotes

class TokenListIterator:
    """ Token List Iterator.
        - Purpose: to traverse tokenized fact, preserving the current token.
        - Motivation: Unlike the common "stateless" iterator made for use in a for-statement,
          the "stateful" Token List Iterator prefers explicit next() usage,
          such as when passed and returned between functions (each specializing in part of the parsing).
          The current element (yielded by next) is still available inside.
    """

    def __init__(self,
         tokens: Iterable[str] | Any,
         titleForErrorMessage: Optional[str] = None
    ):
        """ to INITIALIZE Token List Iterator
            - Exported
            - Input: tokens
            - Contains: string token
            - Input [Opt]: error message title
        """
        # [Opt]: to convert Token List Iterator tokens to list
        if not isinstance(tokens, list):
            tokens = list(tokens)
        self.tokens = tokens
        # to append sentinel to token list
        self.tokens.append(endToken)
        # to create an iterator over the token list
        self.itr = iter(tokens)
        # to get the first token
        self.token = next(self.itr)
        # [Esc Error]: "Premature en0d"
        if self.token == endToken and titleForErrorMessage:
            raise Error(f'Missing {titleForErrorMessage}')

    def __next__(self)-> str:
        """ to EXTRACT next token losslessly
            - Exported
            - Output: string token
        """
        # [Guard]: to get next token
        try:
            self.token = next(self.itr)
        # [Esc Error]: "End of iteration"
        except StopIteration:
            raise
        return self.token

    def atEnd(self)-> bool:
        """ to tell if Token List Iterator is at end
            - Exported
            - Output: result
        """
        return self.token == endToken

    def __normalize(self)-> list[str]:
        """ to normalize Token List Iterator
            - Output: "tokens -- edited"
        """
        tokens = []
        # [Rpt]: to flatten-out token
        while self.token != endToken:
            # [Alt bracket]: to glue bracket to flattenned token-list 
            if tokens and (tokens[-1] in '<([' or self.token in '>)]'):
                tokens[-1] += self.token
            # [Alt period pending]: to glue token to flattened token-list
            elif tokens and (self.token == '.' or tokens[-1] == '.' or (len(tokens[-1]) >= 2 and tokens[-1][-2].isdigit() and self.token.isdigit())):
                tokens[-1] += self.token
            # [Alt normal token]: to append token to flattened token-list
            else:
                tokens.append(self.token)
            # [Msg]: to EXTRACT next token losslessly
            next(self)
        return tokens

    def __str__(self)-> str:
        """ to translate Token List Iterator to string as is
            - Exported
            - Output: result
        """
        # [Msg]: to normalize Token List Iterator
        tokens = self.__normalize()
        return ' '.join(tokens)

    def __iter__(self)-> Iterator[str]:
        """ to TRAVERSE Token List Iterator
            - Output: result
        """
        # [Rpt]: to do traverse Token List
        while self.token != endToken:
            yield self.token
            # [Msg]: to EXTRACT next token losslessly
            next(self)

    def unquote(self)-> str:
        """ to translate Token List Iterator to string removing quotes
            - Exported
            - Output: "string" 
        """
        # [Msg]: to normalize Token List Iterator
        tokens = self.__normalize()
        # [Esc Done]: "Empty"
        if not tokens: return ''
        # [Opt]: to strip quotes from token list
        if tokens[0] in ('"', "'") and tokens[-1] == tokens[0]:
            tokens = tokens[1:-1]
        return ' '.join(tokens)


# Below: Token List short-cuts
# ----------------------------

def parsePositiveNumber(itr: TokenListIterator) -> int:
    """ to parse positive number
        - Input: token list iterator
        - Output: positive integer
    """
    # [Esc Done]: "Empty"
    if not itr.token: return 0
    result = int(itr.token)
    # [Msg]: to EXTRACT next token losslessly
    next(itr)
    return result

def parseNumber(itr: TokenListIterator) -> int:
    """ to parse number
        - Input: token list iterator
        - Output: integer
    """
    # [Esc Done]: "Empty"
    if not itr.token: return 0
    isNegative = False
    # [Opt "Signed"]: to indicate parsed number negative
    if itr.token in '-+':
        isNegative = (itr.token == '-')
        next(itr)
    # [Msg]: to convert token to integer
    result = int(itr.token)
    # [Msg]: to EXTRACT next token losslessly
    next(itr)
    # [Opt]: to negate parsed number
    if isNegative:
        result *= -1
    return result

def parsePercentNumber(
    itr: TokenListIterator,
)-> int:
    """ to parse percent number
        - Input: token list iterator
        - Output: percent number
    """
    # [Msg]: to parse positive number
    result = parsePositiveNumber(itr)
    # [Opt "Percent sign"]: to EXTRACT next token losslessly
    if itr.token == '%':
        next(itr)
    return result

def parseQuotedName(
    itr: TokenListIterator,
    delimiters: str = ''  # default delimiter characters (ignored if sLabel is a quote)
) -> str:
    """ to parse name (space-separated words)
        - Input: token list iterator
        - Input [Opt space]: delimiter characters
        - Output: unquoted string
    """
    # [Msg]: to parse unique entity name
    return parseUniqueEntityName(itr, delimiters)

def parseUniqueEntityName(
    itr: Optional[TokenListIterator],
    delimiter: Optional[str | Iterable[str]] = endToken
)-> str:
    """ to parse unique entity name
        - Input: itr
        - Input [Opt "endToken"]: delimiter
        - Output: result
    """
    # [Esc Done]: "Empty"
    if not itr: return ''
    # [Esc Done]: "At end"
    if itr.atEnd(): return ''
    # [Alt]: to split unique entity name for tokenization
    if delimiter:
        # [Alt "string"]: to enclose unique entity name delimiter in list
        if type(delimiter) is str:
            delimiters = [delimiter]
        # [Alt "not string"]: to convert unique entity name delimiter to list
        else:
            delimiters = list(delimiter)
        # [Opt]: to add the nd-token to unique entity name delimiter list
        if endToken not in delimiters:
            delimiters.append(endToken)
    # [Alt]: to set unique entity delimiters to the end-token
    else:
        delimiters = [endToken]
    tokens, quote = [], ''
    # [Opt "Quotes"]: to skip leading unique entity name quote
    if itr.token in quotes:
        delimiters.append(itr.token)
        quote = itr.token
        # [Msg]: to EXTRACT next token losslessly
        next(itr)
    # [Rpt]: to add token to unique entity name
    while itr.token not in delimiters:
        # [Alt "Bracket"]: to glue bracket to unique entity name tail
        if tokens and (tokens[-1] in '([' or itr.token in ')]'):
            tokens[-1] += itr.token
        # [Alt "Not bracket"]: to append token to unique entity name
        else:
            tokens.append(itr.token)
        # [Msg]: to EXTRACT next token losslessly
        next(itr)
    # [Opt "Closing quote"]: to EXTRACT next token losslessly
    if quote and itr.token == quote:
        next(itr)
    # [Msg]: to clean end of string
    return cleanEnd(' '.join(tokens))

def parseHierarchicalNumber(
    itr: TokenListIterator,
)-> list[str]:
    """ to parse hierarchical number
    """
    # [Scan; Opt]: to pick individual number from tokenized hierarchical number
    return [x for x in itr if x != '.']

def parseDesignPath(itr: TokenListIterator)-> list[str]:
    """ to parse design path
        - Input: itr
        - Output: result
    """
    result = []
    # [Scan "tokens"]: to extract design path components
    for token in itr:
        # [Alt "path delimiter"]: to start next path component
        if token == '/':
            result.append('')
        # [Alt "initial token"]: to set first path component
        elif not result:
            result.append(token)
        # [Alt "continuing token"]: to append token to current path component
        elif result[-1]:
            result[-1] += ' ' + token
        # [Alt]: to set current path component
        else:
            result[-1] = token
    return result


class TokenizedFact:
    """ Tokenized Fact
        - Purpose: to parse raw Labeled-fact to its syntactic elements
    """
    bracketedItemTokenPattern = re.compile(r'".*?"|\'.*?\'|;|\]|[^"\';\]]+')

    def __init__(self,
         rawFact: RawFact | str,
         candidateLabels: list[str],
         indent: int = 0,
         fileName: str = '',
         lineNumber: int = 0,
         isImporting: bool = False # deprecated
    ):
        """ to INITIALIZE Tokenized Fact
            - Input: raw Fact
            - Input: candidate labels
            - Input: indent
            - Input: file name
            - Input: line number
            - Input: is importing
        """
        self.label: str = ''
        # Contains [1:0-N by Value]: label modifier Token List Iterators [role "label modifier"]
        self.labelModifierTokenItrs: list[TokenListIterator] = []
        # Contains [1:0-1 by Value]: argument Token List Iterator [role "argument"]
        self.argumentTokenItr: Optional[TokenListIterator] = None
        # Contains [1:0-N by Value]: argument modifier Token List Iterators [role "argument modifier"]
        self.argModifierTokenItrs: list[TokenListIterator] = []
        self.designPath: list[tuple[str, Any]] = []
        self.fileName: Path = Path(fileName)
        self.lineNum: int = lineNumber
        self.isImporting: bool = isImporting  # deprecated
        self.indent: int = indent
        self.isFirst: bool = False
        # [opt]: to set Raw Tokenized Fact from string
        if not isinstance(rawFact, RawFact):
            line: str = rawFact
            # [Msg]: to INITIALIZE Raw Fact
            rawFact = RawFact()
            # [Msg]: to parse one Labeled Fact raw elements from Fact stream
            rawFact.fromCompositeFact(line, [])
        # Contains [1:1 by Value]: Raw Fact
        self.rawFact: RawFact = rawFact
        # [Msg]: to parse Tokenized Fact label
        self.parseLabel(candidateLabels)

    def parseLabel(self, candidateLabels: list[str]):
        """ to parse Tokenized Fact label
            - definitive [Part]
            - Input: candidate Labels
        """
        self.label = ''
        # [Esc]: candidate Labels and label of rest
        if candidateLabels and self.rawFact.label not in candidateLabels:
            # [Msg]: to find longest colon-less label candidate
            candidates = sorted(
                [x for x in candidateLabels if self.rawFact.label.startswith(x)], 
                key=lambda x: -len(x)
            )
            # [Esc Error]: "Invalid label in fact"
            if not candidates:
                raise Error('Invalid label in fact', [
                    ('Label', self.rawFact.label),
                    ('File', f'{self.rawFact.fileName}:{self.rawFact.lineNumber}'),
                ])
            # [Msg]: to trim colon-less label
            raw_label = getattr(self.rawFact, 'rawLabel', self.rawFact.label)
            arg = raw_label[len(candidates[0]):].lstrip()
            self.rawFact.label = candidates[0]
            # to return label excess to argument
            self.rawFact.arg = ' '.join([arg, self.rawFact.arg]).strip()
        self.label = self.rawFact.label

    def getFirstLabelModifier(self)->Optional[TokenListIterator]:
        """ to get first label modifier from Tokenized Fact
            - Output: result
        """
        # [Esc]: not self label Modifier Token Itrs
        if not self.labelModifierTokenItrs: return None
        return self.labelModifierTokenItrs[0]

    def getFirstArgModifier(self)->Optional[TokenListIterator]:
        """ to get first argument modifier from Tokenized Fact
            - Output: result
        """
        # [Esc]: not self arg Modifier Token Itrs
        if not self.argModifierTokenItrs: return None
        return self.argModifierTokenItrs[0]

    def getParent(self)-> tuple[str, Any]:
        """ to get parent in path to Tokenized Fact
            - Output: result
            - Contains: label
            - Contains: parent object
        """
        return self.designPath[-1] if self.designPath else ('', None)

    def getArgumentAsText(self, isToUnquote: bool=False)-> str:
        """ to get argument of Tokenized Fact as text
            - definitive
            - Input [Opt "False"]: is To Unquote
            - Output: argument text
        """
        # [Esc]: not self argument Token Itr
        if not self.argumentTokenItr: return ''
        return (
            self.argumentTokenItr.unquote() if isToUnquote 
            else str(self.argumentTokenItr)
        )

    def getFirstArgModifierAsText(self, isToUnquote: bool=False)-> str:
        """ to get first argument modifier of Tokenized Fact as text
            - Input [Opt "False"]: is To Unquote
            - Output: argument modifier text
        """
        # [Esc]: not self arg Modifier Token Itrs
        if not self.argModifierTokenItrs: return ''
        return (
            self.argModifierTokenItrs[0].unquote() if isToUnquote 
            else str(self.argModifierTokenItrs[0])
        )

    def getFirstLabelModifierAsText(self, isToUnquote: bool=False)-> str:
        """ to get first label modifier of Tokenized Fact as text
            - Input [Opt "False"]: is To Unquote
            - Output: label modifier text
        """
        # [Esc]: not self label Modifier Token Itrs
        if not self.labelModifierTokenItrs: return ''
        return (
            self.labelModifierTokenItrs[0].unquote() if isToUnquote 
            else str(self.labelModifierTokenItrs[0])
        )
