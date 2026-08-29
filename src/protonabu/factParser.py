""" Module: Protonabu Common Syntax
    - Intent: to define common tokenizers for Protonabu usage
    - Author: Avner Ben
        - Created: 1-Apr-2017
        - Improved: 3-Mar-2026
        - Improved: 26-Aug-2026
            - Prepared for release
"""

from pathlib import Path
import string
import re
from pyparsing import (
    Word,
    CaselessKeyword as Kwd,
    Or,
    ZeroOrMore,
    OneOrMore,
    Optional as Opt,
    ParseException
)
from typing import Any, Optional, Iterable

from .util.error import Error, ParsingError
from .util.stringUtil import cleanEnd
from .rawFact import RawFact

errMsgPattern = re.compile(r'\(line:\d+, col:(\d+)\)')


def getErrMsg(error: ParseException, where: Optional[str] = None):
    """ to get error msg
        - Input: error
        - Input [Opt "None"]: where
        - Output: result
    """
    rawMsg, msg = str(error), 'Invalid syntax'
    # [Esc Done]: end-of-text message
    if rawMsg.startswith('Expected end of text'):
        # to replace end-of-text error message
        return 'Excess information in line'
    # [Opt raw message found]: to update error message with location
    if (matched := errMsgPattern.search(rawMsg)):
        msg += f' (at column {matched.group(1)}'
        # [Opt]: to append location to error message
        if where:
            msg += f' in {where}'
        msg += ')'
    return msg


tokenLegend: dict[Any, str] = {}

# below: parsing constants:
# -------------------------
lowerCase = string.ascii_lowercase
upperCase = string.ascii_uppercase
alphaLetters = lowerCase + upperCase
initLetters = alphaLetters + '_'
digits = string.digits
alphaNum = alphaLetters + digits
emailLetters = initLetters + digits + '.'
wordLetters = initLetters + "-+#/<>'" + digits
quotes = '\'"'
tQuotes = tuple(quotes)
separators = '/\\'
tSeparators = tuple([x for x in separators])
printables = string.printable.replace(' ', '').replace('"', '')
ellipsis = '...'
endToken = ''

# below: primitive tokens:
# ------------------------
comma = Word(',', exact=1)
semicolon = Word(';', exact=1)
period = Word('.', exact=1)
colon = Word(':', exact=1)
lBracket = Word('(', exact=1)
rBracket = Word(')', exact=1)
lSqrBracket = Word('[', exact=1)
rSqrBracket = Word(']', exact=1)
lTriBracket = Word('<', exact=1)
rTriBracket = Word('>', exact=1)
dQuote = Word('"', exact=1)
sQuote = Word("'", exact=1)
exclam = Word('!', exact=1)
equals = Word('=', exact=1)
hyphen = Word('-', exact=1)
percent = Word('%', exact=1)
aroba = Word('@', exact=1)
slash = Word('/', exact=1)
doubleHyphen = Kwd('--')

# Below: basic types
# ------------------
positiveNumber = Word(digits)
tokenLegend[positiveNumber] = """
Sequence of digits
"""
number = \
    Opt(Word('-+', exact=1)) \
    + Word(digits)
tokenLegend[number] = """
Sequence of digits, optionally preceded by + or -
"""
positiveFraction = Or((
    Word('.', digits),
    positiveNumber + Word('.', digits),
    number
))
tokenLegend[positiveFraction] = """
The symbol ., optionally preceded by sequence of digits and/or followed by sequence of digits
"""
fraction = \
    Opt(Word('-+', exact=1)) \
    + positiveFraction
tokenLegend[fraction] = """
The symbol ., optionally preceded by sequence of digits and/or followed by sequence of digits and (the whole) optionally preceded by + or -
"""
percentNumber = \
    positiveNumber \
    + Opt(percent)
tokenLegend[percentNumber] = """
Positive number between 0-100, optionally followed by %
"""
boolean = Or((
    Kwd('ON'),
    Kwd('OFF'),
))
tokenLegend[boolean] = """
One of: ON or OFF
"""
labelToken = Word(alphaLetters, alphaNum)
LabelName = OneOrMore(labelToken)
tokenLegend[LabelName] = """
sequence of words, consisting of lower-case, upper case or digit, and beginning with lower-case or upper case letter
"""
programmaticName = Word(initLetters, wordLetters)
tokenLegend[programmaticName] = """
Sequence of letters, , and beginning with lower-case or upper-case letter or _, and the rest consisting of lower-case, upper-case, digits, or the symbol _, -, + and #
"""
word = Opt(lBracket) + Word(wordLetters) + Opt(rBracket)  # todo: does not start with digit
tokenLegend[word] = """
sequnce of letters, consisting of lower-case, upper-case, digit or the symbol _, -, + and #. Optionally enclosed in round brackets
"""
uniqueEntityName = OneOrMore(word)
tokenLegend[uniqueEntityName] = """
Sequence of words, beginning with programmatic, allowing round brackets (around one or more whole words) and optionally one '>'
"""
quotedName = Or((
    dQuote + Opt(uniqueEntityName) + dQuote,
    uniqueEntityName
))
tokenLegend[quotedName] = """
Sequence of words, beginning with programmatic, allowing round brackets (around one or more whole words) and (the whole) optionally enclosed within double quotes
"""
value = Or((
    fraction,
    number,
    quotedName
))
tokenLegend[value] = """
One of: fraction, number or quoted name (as applies)
"""
sequenceNumber = Or((
    positiveNumber,
    Word(lowerCase, exact=1),
    Word(upperCase, exact=1)
))
tokenLegend[sequenceNumber] = """
One of: positive number, lower-case letter of upper-case letter (as applies)
"""
hierarchicalNumber = \
    sequenceNumber + \
    ZeroOrMore(
        period + sequenceNumber
    )
tokenLegend[hierarchicalNumber] = """
Sequence of positive numbers or letters, separated by dots. Usually enumerating a bulleted document item
"""
printables_d = string.printable.replace(' ', '').replace('"', '')
printableName_d = Word(printables_d)
text_d = OneOrMore(printableName_d)

printableName = Word(printables)
tokenLegend[printableName] = """
Sequence of letters consisting of lower-case, upper case, digit or punctuation, excluding space and quotes
"""
text = OneOrMore(printableName)
emptyQuotedText = dQuote + dQuote
tokenLegend[text] = """
sequence of words, consisting of lower-case, upper case, digit or punctuation, excluding space and quotes
"""
quotedText = Or((
    dQuote + text_d + dQuote,
    text,
    emptyQuotedText
))
tokenLegend[quotedText] = """
sequence of words, consisting of lower-case, upper case, digit or punctuation, excluding space and double quotes and (the whole) optionally enclosed within double quotes
"""
fileName = OneOrMore(Word(wordLetters + '.'))  # ?
tokenLegend[fileName] = """
sequence of words, each consisting of lower-case, upper-case, digit or the symbols _, -, +, #
"""
fileSeparator = Or(
    [Word(x, exact=1) for x in separators]
)
pathName = \
    Opt(
        Word(lowerCase + upperCase, exact=1) + colon
    ) \
    + Opt(fileSeparator) \
    + ZeroOrMore(fileName + fileSeparator) \
    + Opt(fileName)
tokenLegend[pathName] = r"""
Sequence of file-names (see item), separated by / or \ and optionally preceded by lower-case or upper-case followed by colon and/or the file separator / or \
"""
quotedPathName = Or((
    dQuote + pathName + dQuote,
    pathName
))
tokenLegend[quotedPathName] = r"""
Sequence of file-names (see item), separated by / or \ and optionally preceded by lower-case or upper-case followed by colon and/or the file separator / or \ and (the whole) optionally enclosed within double quotes
"""

monthNameDate = \
    positiveNumber + '-' + Or((
        Kwd('JAN'),
        Kwd('FEB'),
        Kwd('MAR'),
        Kwd('APR'),
        Kwd('MAY'),
        Kwd('JUN'),
        Kwd('JUL'),
        Kwd('AUG'),
        Kwd('SEP'),
        Kwd('OCT'),
        Kwd('NOV'),
        Kwd('DEC')
    )) \
    + '-' + positiveNumber
tokenLegend[monthNameDate] = """
Positive number day, three-letter month name and positive number year, separated by -. E.g. 1-JAN-2011
"""
monthNumberDate = \
    positiveNumber \
    + '-' + positiveNumber \
    + '-' + positiveNumber
tokenLegend[monthNumberDate] = """
Positive number day, positive number month and positive number year, separated by -. E.g. 1-1-2011
"""
documentDate = Or((
    monthNameDate,
    monthNumberDate
))
tokenLegend[documentDate] = """
Either of: month-name-date or month-number-date (see items)
"""
email = \
    Word(emailLetters) \
    + aroba \
    + Word(emailLetters)
tokenLegend[email] = """
two sequences of letters consisting of lower-case, upper-case, digit or the symbol _ or ., separated by @
"""
designPath = \
    LabelName \
    + ZeroOrMore(
        slash + LabelName
    )
tokenLegend[designPath] = """
Sequence of label-names (see item), separated by / (between spaces)
"""

class TokenListIterator:
    """ Token List Iterator.
        - Purpose: to TRAVERSE tokenized fact, retaining the current label.
        - Motivation: Unlike the common "stateless" iterator made for use in a "for statement",
          the "stateful" Token List Iterator prefers explicit next() usage,
          such as when passed and returned between functions (each specializing in part of the parsing).
          The current element (yielded by next) is still available inside
    """

    def __init__(self,
         tokens: list[str],
         titleForErrorMessage: Optional[str] = None
    ):
        """ to INIITIALIZE Token List Iterator
            - Input: tokens
            - Input [Opt "None"]: title For Error Message
        """
        # [Opt]: to convert input tokens to list
        if not isinstance(tokens, list):
            tokens = list(tokens)
        self.tokens = tokens
        self.tokens.append(endToken)
        self.itr = iter(tokens)
        self.token = next(self.itr)
        # [Esc Error]: "self token equals end Token and title For Error Message"
        if self.token == endToken and titleForErrorMessage:
            raise Error(f'Missing {titleForErrorMessage}')

    def __next__(self):
        """ to advance token list iterator retaining next label
            - Output: result
            - definitive [Part]
        """
        # [Guard]: to progress in internal token list
        try:
            self.token = next(self.itr)
        # [Esc]: StopIteration
        except StopIteration:
            raise
        return self.token

    def toNext(self):
        """ to progress in Token list iterator retaining next token
            - Output: result
        """
        token = self.token
        # [Msg]: to advance token list iterator retaining next label
        next(self)
        return token

    def atEnd(self):
        """ to tell if Token List Iterator is at end
            - Output: result
        """
        return self.token == endToken

    def _collectTokens(self) -> list[str]:
        """ to collect tokens from Token List Iterator
            - Output: tokens
        """
        tokens = []
        # [Rpt]: to add token to token-list in iterator
        while self.token != endToken:
            # [Alt]: to append token to last token in iterator
            if tokens and (tokens[-1] in '<([' or self.token in '>)]'):
                tokens[-1] += self.token
            # [Alt]: to append token to token-list in iterator
            else:
                tokens.append(self.token)
            # [Msg]: to advance token list iterator retaining next label
            next(self)
        return tokens

    def __str__(self):
        """ to translate Token List Iterator to string without parsing the content
            - Output: result
        """
        # [Msg]: to collect tokens from Token List Iterator
        return ' '.join(self._collectTokens())

    def __iter__(self):
        """ to iterate over Token List Iterator content
        """
        # [Rpt]: to TRAVERSE Token List Iterator
        while self.token != endToken:
            yield self.token
            next(self)

    def unquote(self):
        """ to translate Token List Iterator to string removing quotes
            - Output: result
            - definitive
        """
        # [Msg]: to collect tokens from Token List Iterator
        tokens = self._collectTokens()
        # [Esc]: no tokens
        if not tokens: return ''
        # [Opt]: to set tokens from unquoted token list
        if tokens[0] in ('"', "'") and tokens[-1] == tokens[0]:
            tokens = tokens[1:-1]
        return ' '.join(tokens)

    def unquotePathName(self):
        """ to unquote path name
            - Output: result
        """
        return self.unquote().replace(' / ', '/').replace(' \\ ', "\\")


######################################################################## obsolete...
# Below: Generic line parsers

def parseBoolean(
    itr: TokenListIterator,
    default: bool=False
)-> bool:
    """ to parse boolean
        - Input: itr
        - Input [Opt "False"]: default result
    """
    # [Esc Done]: no token
    if not itr.token: return default
    result = (itr.token.upper() == 'ON')
    # [Msg]: to advance token list iterator retaining next label
    next(itr)
    return result

def parsePositiveNumber(
    itr: TokenListIterator,
)-> int:
    """ to parse positive number
        - Input: itr
        - Output: result
    """
    # [Esc Done]: no token
    if not itr.token: return 0
    result = int(itr.token)
    # [Msg]: to advance token list iterator retaining next label
    next(itr)
    return result

def parseNumber(
    itr: TokenListIterator,
)-> int:
    """ to parse number
        - Input: itr
        - Output: result
    """
    # [Esc Done]: No number
    if not itr.token: return 0
    isNegative = False
    # [Opt]: to set number token negative 
    if itr.token in '-+':
        isNegative = (itr.token == '-')
        # [Msg]: to advance token list iterator retaining next label
        next(itr)
    result = int(itr.token)
    # [Msg]: to advance token list iterator retaining next label
    next(itr)
    # [Opt]: to negate result token
    if isNegative:
        result *= -1
    return result

def parsePercentNumber(
    itr: TokenListIterator,
)-> int:
    """ to parse percent number
        - Input: itr
        - Output: result
    """
    # [Msg]:  to parse positive number
    result = parsePositiveNumber(itr)
    # [Msg; Opt "percent"]: to advance token list iterator retaining next label
    if itr.token == '%':
        next(itr)
    return result

def parseFraction(
    itr: TokenListIterator,
)-> float:
    """ to parse fraction
        - Input: itr
        - Output: result
    """
    if not itr.token: return 0
    result = 0.0
    isNegative = False
    # [Opt]: to detect signed number token
    if itr.token in '-+':
        isNegative = (itr.token == '-')
        # [Msg]: to advance token list iterator retaining next label
        next(itr)
    # [Opt]: to convert token to floating-point number
    if not itr.token.startswith('.'):
        result = float(itr.token)
        # [Msg]: to advance token list iterator retaining next label
        next(itr)
    # [Opt]: to add fractional part toekn to floating-point number
    if itr.token.startswith('.'):
        result += float(itr.token)
    # [Opt]: to negate floating-point toke result
    if isNegative:
        result *= -1.0
    return result

def parseQuotedName(
    itr: TokenListIterator,
    delimiters: str = ''  # default delimiter characters (ignored if sLabel is a quote)
) -> str:
    ''' to parse name (space-separated words)
    '''
    # [Msg]: to parse unique entity name
    return parseUniqueEntityName(itr, delimiters)

def parseUniqueEntityName(
    itr: Optional[TokenListIterator],
    delimiter: Optional[str | Iterable[str]] = endToken 
)-> str:
    # [Esc]: Nothing to read
    """ to parse unique entity name
        - Input: itr
        - Input [Opt "endToken"]: delimiter
        - Output: result
    """
    # [Esc]: Nothing to read
    if not itr: return ''
    # [Esc]: At end
    if itr.atEnd(): return ''
    # [Alt]: to set delimiters from input argument
    if delimiter:
        # [Alt]: to wrap singular tokenization input in list
        if type(delimiter) is str:
            delimiters = [delimiter]
        # [Alt]: to wrap tokenization input in list
        else:
            delimiters = list(delimiter)
        # [Opt]: to ensure end token in delimiters list
        if endToken not in delimiters:
            delimiters.append(endToken)
    # [Alt]: to set given tokenization delimiter
    else:
        delimiters = [endToken]
    tokens, quote = [], ''
    # [Opt]: to detect quoted token list
    if itr.token in quotes:
        delimiters.append(itr.token)
        quote = itr.token
        # [Msg]: to advance token list iterator retaining next label
        next(itr)
    # [Rpt]: to add token to unique entity token list
    while itr.token not in delimiters:
        # [Alt]: to append token to last  unique entity token list
        if tokens and (tokens[-1] in '([' or itr.token in ')]'):
            tokens[-1] += itr.token
        # [Alt]: to set unique entity token
        else:
            tokens.append(itr.token)
        # [Msg]: to advance token list iterator retaining next label
        next(itr)
    # [Msg; Opt duplicate]: to advance token list iterator retaining next label
    if quote and itr.token == quote:
        next(itr)
    # [msg]: to clean end of string
    return cleanEnd(' '.join(tokens))

def parseText(itr: TokenListIterator):
    """ to parse text
        - Input: itr
        - Output: result
    """
    result, delimiters, quote = [], [endToken], ''
    # [Alt]: to detect quote in text token list
    if itr.token in quotes:
        delimiters.append(itr.token)
        # [Msg]: to advance token list iterator retaining next label
        next(itr)
    # [Alt]: to quote-starting token in text token list
    elif itr.token.startswith(tQuotes):
        quote = itr.token[0]
        delimiters.append(quote)
        itr.token = itr.token[1:].lstrip()
    # [Rpt]: to process token in text token list
    while itr.token not in delimiters and itr.token != endToken:
        # [Esc Done]: quote in token
        # to split quote-containing token in text token list
        if quote and quote in itr.token:
            pre, post = itr.token.split(quote, 1)
            pre, post = pre.rstrip(), post.lstrip()
            # [Opt]: to add pre token to text token list
            if pre:
                result.append(pre)
            # [Opt]: to prepare for end quote in text token list 
            if post:
                itr.token = post
            break
        result.append(itr.token)
        # [Msg]: to advance token list iterator retaining next label
        next(itr)
    # [Opt; Msg]: to advance token list iterator retaining next label
    if itr.token and itr.token == quote:
        next(itr)
    result = ' '.join(result)
    result = cleanEnd(result).rstrip()
    # to return quoted string result
    return result

def parseHierarchicalNumber(
    itr: TokenListIterator,
)-> list[str]:
    ''' to parse hierarchical number
    '''
    # [Scan; Opt]: to pick non-period token from Token List Iterator inner list
    return [x for x in itr if x != '.']

def parsePathName(
    itr: TokenListIterator,
    delimiters: str='' # default delimiter characters (ignored if sLabel is a quote)
)-> str:
    ''' to parse file path-name
    '''
    sName, quote = '', None
    # [Opt quoted]: to set pathname delimites and quote utomatically
    if itr.token in ['"', "'"]:
        delimiters = itr.token
        quote = itr.token
        # [Msg]: to advance token list iterator retaining next label
        next(itr)
    sep = separators + ':'
    # [Scan]: to collect condition
    while itr.token not in delimiters and itr.token != endToken:
        if sName != '' and itr.token not in sep and not sName.endswith(tSeparators):
            sName += ' '
        sName += itr.token
        next(itr)
    # [Msg; Opt quote]: to advance token list iterator retaining next label
    if itr.token == quote:
        next(itr)
    return sName

def parseDesignPath(itr: TokenListIterator)-> list[str]:
    """ to parse design path
        - Input: itr
        - Output: result
    """
    result = []
    # [Scan]: to process token in design-path token list
    for token in itr:
        # [Alt]: to append separator to design-path token list
        if token == '/':
            result.append('')
        # [Alt]: to append path-element to design-path token-list
        elif not result:
            result.append(token)
        # [Alt]: to append spacer to design-path token-list
        elif result[-1]:
            result[-1] += ' ' + token
        # [Alt]: to set last design-path element token
        else:
            result[-1] = token
    return result

#####################################################################

class TokenizedFact:
    """ Tokenized Fact
        - Purpose: to parse raw Labeled-fact to its syntactic elements
    """
    bracketedItemTokenPattern = re.compile(r'".*?"|\'.*?\'|;|\]|[^"\';\]]+')

    def __init__(
        self,
        rawFact: RawFact | str,
        candidateLabels: list[str],
        indent: int = 0,
        fileName: str = '',
        lineNumber: int = 0,
        isImporting: bool = False
    ):
        """ to INITIALIZE Tokenized Fact
            - Input: raw Fact
            - Input: candidate Labels
            - Input [Opt "0"]: indent
            - Input [Opt ""]: file Name
            - Input [Opt "0"]: line Number
            - Input [Opt "False"]: is Importing
        """
        ## Tokens:
        ## -------
        self.label: str = ''
        self.labelModifierTokenItrs: list[TokenListIterator] = []
        self.argumentTokenItr: Optional[TokenListIterator] = None
        self.argModifierTokenItrs: list[TokenListIterator] = []
        self.designPath: list[tuple[str, Any]] = []
        ## Info:
        ## -----
        self.fileName: Path = Path(fileName)
        self.lineNum = lineNumber
        self.isImporting = isImporting
        ## State:
        ## -----
        self.indent: int = indent
        self.isFirst: bool = False
        # [opt]: to set Raw Tokenized Fact from string
        if not isinstance(rawFact, RawFact):
            line: str = rawFact
            # [Msg]: to INITIALIZE Raw Fact
            rawFact = RawFact()
            # [Msg]: to parse raw Labeled Fact from one or more consecutive raw Fact lines
            rawFact.fromCompositeFact(line, [])
        self.rawFact: RawFact = rawFact
        # [Msg]: to parse Tokenized Fact label
        self.parseLabel(candidateLabels)

    def parseLabel(self,
           candidateLabels: list[str],
           isLabelMandatory: bool=True
        ):
        """ to parse Tokenized Fact label
            - Input: candidate Labels
            - Input [Opt "True"]: is Label Mandatory
            - definitive [Part]
        """
        self.label = ''
        # [Esc]: Error
        if candidateLabels and self.rawFact.label not in candidateLabels:
            raise Error('Invalid label in fact', [
                ('Label', self.rawFact.label),
                ('File', f'{self.rawFact.fileName}:{self.rawFact.lineNumber}'),
            ])
        self.label = self.rawFact.label

    def getFirstLabelModifier(self):
        """ to get first label modifier from Tokenized Fact
            - Output: result
        """
        # [Esc Done]: Empty
        if not self.labelModifierTokenItrs: return None
        return self.labelModifierTokenItrs[0]

    def getFirstArgModifier(self):
        """ to get first argument modifier from Tokenized Fact
            - Output: result
        """
        # [Esc Done]: Empty
        if not self.argModifierTokenItrs: return None
        return self.argModifierTokenItrs[0]

    def getParent(self)-> tuple[str, Any]:
        """ to get parent in path to Tokenized Fact
            - Output: result
        """
        # [Esc Done]: Empty
        return self.designPath[-1] if self.designPath else ('', None)

    def getArgumentAsText(self, isToUnquote: bool=False)-> str:
        """ to get argument of Tokenized Fact as text
            - Input [Opt "False"]: is To Unquote
            - Output: result
        """
        # [Esc Done]: Empty
        if not self.argumentTokenItr: return ''
        return (
            self.argumentTokenItr.unquote() if isToUnquote 
            else str(self.argumentTokenItr)
        )

    def getFirstArgModifierAsText(self, isToUnquote: bool=False)-> str:
        """ to get first argument modifier of Tokenized Fact as text
            - Input [Opt "False"]: is To Unquote
            - Output: result
        """
        # [Esc Done]: Empty
        if not self.argModifierTokenItrs: return ''
        return (
            self.argModifierTokenItrs[0].unquote() if isToUnquote 
            else str(self.argModifierTokenItrs[0])
        )

    def getFirstLabelModifierAsText(self, isToUnquote: bool=False)-> str:
        """ to get first label modifier of Tokenized Fact as text
            - Input [Opt "False"]: is To Unquote
            - Output: result
        """
        # [Esc Done]: Empty
        if not self.labelModifierTokenItrs: return ''
        return (
            self.labelModifierTokenItrs[0].unquote() if isToUnquote 
            else str(self.labelModifierTokenItrs[0])
        )

