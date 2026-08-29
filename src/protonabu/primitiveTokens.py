""" Module: Primitive Tokens
    - Purpose: Primitive PyParsing-based tokens used by Protonabu
    - Author: Avner Ben
        - Created: 1-Apr-2017
        - Revised: 24-Jun-2026
            - Separated from fact Parser
        - Improved: 26-Aug-2026
            - Prepared for release
"""

import string
from pyparsing import (
    Word,
    CaselessKeyword as Kwd, # Case-insensitive keyword
    Or,
    ZeroOrMore,
    OneOrMore,
    Optional as Opt # to prevent ambiguity with Python's typing
)
from typing import Any

# to prepare to document Protonabu tokenizers
tokenLegend: dict[Any, str] = {}

# Below: Constants
# ----------------
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

# Below: Primitive tokens
# -----------------------
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
Sequence of letters, beginning with lower-case or upper-case letter or _, and the rest consisting of lower-case, upper-case, digits, or the symbol _, -, + and #
"""
word = Opt(lBracket) + Word(wordLetters) + Opt(rBracket)  # todo: does not start with digit
tokenLegend[word] = """
sequnce of letters, consisting of lower-case, upper-case, digit or the symbol _, -, + and #. Optionally enclosed in round brackets
"""
uniqueEntityName = OneOrMore(word)
tokenLegend[uniqueEntityName] = """
Sequence of words, beginning with programmatic name, allowing round brackets (around one or more whole words) and optionally one '>'
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
printableName = Word(printables)
tokenLegend[printableName] = """
Sequence of letters consisting of lower-case, upper case, digit or punctuation, excluding space and quotes
"""
text = OneOrMore(printableName)
emptyQuotedText = dQuote + dQuote
tokenLegend[text] = """
sequence of words, consisting of lower-case, upper case, digit or punctuation, excluding space and double quotes
"""
printables_d = string.printable.replace(' ', '').replace('"', '')
printableName_d = Word(printables_d)
text_d = OneOrMore(printableName_d)

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
tilde = Word('~', exact=1)
pathName = (
    Opt(
        Or((
            Word(lowerCase + upperCase, exact=1) + colon,
            tilde
        ))
    )
    + Opt(fileSeparator)
    + ZeroOrMore(fileName + fileSeparator)
    + Opt(fileName)
)

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

class UnstructuredText:
    """ Unstructured Text Tokenizer
    """
    def parseString(self, s: str, parseAll:bool=True)-> list[str]:
        """ to parse string
            - Input: string to tokenize
            - Input [Opt "True"]: is to parse all
            - Output: list of tokens
        """
        return s.strip().split()
unstructuredText = UnstructuredText()
tokenLegend[unstructuredText] = """
Any combination of Unicode characters, up to end of line
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

# to prepare to ignore basic types in schema documentation
basicTypeNames = [ 
    "positiveNumber",
    "number",
    "fraction",
    "percentNumber",
    "boolean",
    "LabelName",
    "programmaticName",
    "longName",
    "quotedName",
    "value",
    "sequenceNumber",
    "printableName",
    "text",
    "quotedText",
    "fileName",
    "pathName",
    "quotedPathName",
    "monthNameDate",
    "monthNumberDate",
    "documentDate",
    "email",
    "designPath",
]


