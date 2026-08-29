""" Module: Protonabu String Utilities
    - Author: Avner Ben
        - Created: 1-Oct-2005
        - Improved: 1-Jan-2024
        - Improved: 28-Aug-2026
            - Moved here from the Nabu project string utilities
"""

import time
import re
from typing import Iterable, Any, Optional

from .error import Error, InternalError

cleanEndPattern =   re.compile(r'[.,:; ]*$')
unquotePattern =    re.compile(r'^\s*(["\'])(.*)\1\s*')

methodChars = 'abcedfghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789'


class IdCounter:
    """ ID Counter
    """
    _instances: list['IdCounter'] = []

    def __init__(self, prefix: str='group', start: int=0):
        """ to INITIALIZE Visual Required ID Counter
        """
        self.start = start
        self.counter = start
        self.prefix = prefix
        IdCounter._instances.append(self)
        
    def next(self)-> str:
        """ to get next Visual Required ID
        """
        self.counter += 1
        return f'{self.prefix}_{self.counter}'

    @classmethod
    def resetAll(cls):
        """ to reset all initialized ID Counters across modules
        """
        for instance in cls._instances:
            instance.counter = instance.start
        nameMaker.clearRegistries()


class NameMaker:
    """ Name Maker
    """
    abbrevs = {
        'Account': 'Acct',
        'Allocate': 'Alloc',
        'Application': 'App',
        'Argument': 'Arg',
        'Calculate': 'Calc',
        'Change': 'Chg',
        'Character': 'Char',
        'Client': 'Clt',
        'Command': 'Cmd',
        'Communication': 'Comm',
        'Compute': 'Comp',
        'Configure': 'Cfg',
        'Configuration': 'Cfg',
        'Context': 'Ctxt',
        'Control': 'Ctl',
        'Constant': 'Const',
        'Copy': 'Cpy',
        'Convert': 'Cnv',
        'Database': 'Db',
        'Derivative': 'Deriv',
        'Demonstration': 'Demo',
        'Description': 'Desc',
        'Dictionary': 'Dict',
        'Directory': 'Dir',
        'Display': 'Dsp',
        'Division': 'Div',
        'Document': 'Doc',
        'Driver': 'Drvr',
        'Duplicate': 'Dup',
        'Double': 'Dbl',
        'Element': 'Elem',
        'Error': 'Err',
        'Hexadecimal': 'Hex',
        'Exception': 'Excp',
        'Event': 'Evt',
        'Floating': 'Float',
        'Framework': 'Fwk',
        'Function': 'Func',
        'Generation': 'Gen',
        'Hardware': 'Hw',
        'Header': 'Hdr',
        'Identifier': 'Id',
        'Implement': 'Imp',
        'Integer': 'Int',
        'Interface': 'Intf',
        'Library': 'Lib',
        'Manager': 'Mgr',
        'Matrix': 'Mat',
        'Memory': 'Mem',
        'Message': 'Msg',
        'Multiply': 'Mul',
        'Number': 'Num',
        'Parameter': 'Param',
        'Product': 'Prod',
        'Project': 'Proj',
        'Process': 'Proc',
        'Pointer': 'Ptr',
        'Property': 'Prop',
        'Reader': 'Rdr',
        'Realtime': 'Rt',
        'Receiver': 'Rcvr',
        'Record': 'Rec',
        'Release': 'Rel',
        'Repository': 'Repo',
        'Request': 'Req',
        'Response': 'Resp',
        'Report': 'Rpt',
        'Retrieve': 'Rtrv',
        'Runtime': 'Rt',
        'Server': 'Srv',
        'Service': 'Svc',
        'Sequence': 'Seq',
        'Size': 'Sz',
        'Software': 'Sw',
        'Source': 'Src',
        'Standard': 'Std',
        'String': 'Str',
        'System': 'Sys',
        'Table': 'Tbl',
        'Target': 'Tgt',
        'Technique': 'Tech',
        'Utility': 'Util',
        'Variable': 'Var',
        'Vector': 'Vec',
    }
    crossAbbrevs = dict([(x[1], x[0]) for x in abbrevs.items()])
    _magic_methods: dict[str, str] = {}

    @classmethod
    def setMagicMethods(cls, mapping: dict[str, str]):
        """ to register domain-specific magic methods mapping
            - Exported
        """
        cls._magic_methods = dict(mapping)

    @property
    def MAGIC_METHODS(self) -> dict[str, str]:
        """ to get magic methods mapping
        """
        return self._magic_methods

    caps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    delims = ' -_/'
    stLow, endLow = ord('a'), ord('z')
    stUp, endUp = ord('A'), ord('Z')
    stNum, endNum = ord('0'), ord('9')

    def __init__(self):
        """ to INITIALIZE Name Maker
            - Exported
        """
        self._registries: dict[Any, dict[str, Any]] = {}

    def addAbbreviation(self, kwd: str, abbrev: str, addToAbbrevs=True, addToCrossAbbrevs=True):
        """ to add abbreviation for use in programmatic names
            - Exported
        """
        kwd, abbrev = kwd.strip().capitalize(), abbrev.strip().capitalize()
        if addToAbbrevs:
            self.abbrevs[kwd] = abbrev
        if addToCrossAbbrevs:
            self.crossAbbrevs[abbrev] = kwd

    def makeProgrammaticName(self,
        name: str,
        suffix: str = '',
        ignoreLast: str = '',
        capFirst: bool = True,
        isAcronym: bool = False
    ) -> str:
        """ to make programmatic name from literate name
            - Exported
        """
        # [Esc Error]: Missing name
        if not name:
            raise InternalError('Missing name')
        try: suffix = self.abbrevs[suffix]
        except KeyError: pass
        words, curW = [], ''
        ignoreLast = ignoreLast.upper()
        if name.isupper():
            name = name.lower()
        for c in name:
            ordC = ord(c)
            if c in self.delims:
                if curW:
                    words.append(curW)
                    curW = ''
            elif self.stUp <= ordC <= self.endUp or self.stNum <= ordC <= self.endNum:
                if curW:
                    words.append(curW)
                curW = c
            elif self.stLow <= ordC <= self.endLow:
                curW += c
            elif curW:
                words.append(curW)
                curW = ''
        if curW:
            words.append(curW)
        if words and words[-1].upper() == ignoreLast:
            words.remove(words[-1])
        # [Opt]: to remove trailing articles and prepositions
        trailing_to_strip = {'to', 'the', 'a', 'an', 'of', 'at', 'by', 'in', 'on', 'with', 'for', 'from'}
        while words and words[-1].lower() in trailing_to_strip:
            words.pop()
        filtered_words = [w for w in words if w.lower() not in ('to', 'the', 'a', 'an')]
        if filtered_words:
            words = filtered_words
        # [Esc Error]: cannot make programmatic name
        if not words:
            raise Error(f'cannot make programmatic name for "{name}"')
        # [Opt]: to leave name unabbreviated
        # - Reason: single word name
        if len(words) == 1:
            if capFirst: result = words[0][0].upper() + words[0][1:]
            else: result = words[0][0].lower() + words[0][1:]
        # [Opt]: to concatenate capitalized words in name
        else:
            result, start = '', 1
            for word in words:
                if capFirst or not start:
                    preAbbrev = word.capitalize()
                else:
                    preAbbrev = word.lower()
                start = 0
                if preAbbrev in self.abbrevs:
                    result += self.abbrevs[preAbbrev]
                elif (upPreAbbrev := preAbbrev[0].upper() + preAbbrev[1:]) in self.abbrevs:
                    result += self.abbrevs[upPreAbbrev].lower()
                else:
                    result += preAbbrev
            # [Opt]: to make acronym of name
            if len(result) > 32 and isAcronym:
                result = ''
                for word in words:
                    result += word[0].upper()
        if suffix:
            result += suffix
        return result

    def makeUniqueProgrammaticName(
        self,
        name: str,
        scopes: list = None,
        ref: Any = None,
        suffix: str = '',
        ignoreLast: str = '',
        capFirst: bool = True,
        isAcronym: bool = False
    ) -> str:
        """ to make unique programmatic name from literate name
            - Exported
        """
        base_name = self.makeProgrammaticName(
            name,
            suffix=suffix,
            ignoreLast=ignoreLast,
            capFirst=capFirst,
            isAcronym=isAcronym
        )
        if not scopes:
            return base_name
            
        if not isinstance(scopes, (list, tuple)):
            scopes = [scopes]
            
        unique_name = base_name
        counter = 1
        while True:
            collision = False
            for scope in scopes:
                if scope is not None and scope in self._registries:
                    if unique_name in self._registries[scope]:
                        existing_ref = self._registries[scope][unique_name]
                        if ref is None or existing_ref is None or existing_ref is not ref:
                            collision = True
                            break
            if not collision:
                break
            unique_name = f"{base_name}{counter}"
            counter += 1
            
        for scope in scopes:
            if scope is not None:
                if scope not in self._registries:
                    self._registries[scope] = {}
                self._registries[scope][unique_name] = ref
                
        return unique_name

    def register(self, name: str, scopes: list, ref: Any = None):
        """ to register an existing name in the given scopes
            - Exported
        """
        if not scopes:
            return
        if not isinstance(scopes, (list, tuple)):
            scopes = [scopes]
        for scope in scopes:
            if scope is not None:
                if scope not in self._registries:
                    self._registries[scope] = {}
                self._registries[scope][name] = ref

    def clearRegistries(self):
        """ to clear all registries
            - Exported
        """
        self._registries.clear()

    def unMakeProgrammaticName(
            self,
            s: str,
            suffix=None,
            lowerCaseAbbreviations=False,
            upper=False
    ) -> str:
        """ to restore literate name from programmatic name
            - Exported
        """
        if not s: return s
        if upper:
            s = s[0].upper() + s[1:]
        parts = []
        startPos = 0
        # [Scan]: to separate name at delimiter
        for i, c in enumerate(s):
            # [Opt]: to separate name at capital or digit
            if c in self.caps:
                if i > startPos and s[i-1] not in self.caps:
                    parts.append(s[startPos:i])
                    startPos = i
            # [Opt]: to separate name at underscore
            elif c in ["_"]:
                if i > startPos:
                    parts.append(s[startPos:i])
                startPos = i + 1
        # [Opt]: to separate last name
        if startPos < len(s):
            parts.append(s[startPos:])
        if suffix and parts[-1].upper() != suffix.upper():
            parts.append(suffix)
        parts = [x.strip() for x in parts if x.strip()]
        for i, part in enumerate(parts):
            try:
                part = self.crossAbbrevs[part.capitalize()]
                if lowerCaseAbbreviations:
                    part = part[0].lower() + part[1:]
                parts[i] = part
            except KeyError: pass
        result = ' '.join(parts)
        return result

    def translateMagicMethod(self, methodName: str) -> str:
        """ to translate magic method to Nabu capability verb
            - Exported
        """
        if methodName in self.MAGIC_METHODS:
            return self.MAGIC_METHODS[methodName]
        verb = unCamel(methodName).lower().replace('_', ' ')
        return ' '.join(verb.split())

    def processWord(self, name: str) -> str:
        """ to programmatize name
            - Exported
        """
        if ' ' in name:
            return self.makeProgrammaticName(name)
        try:
            return self.abbrevs[name.capitalize()]
        except KeyError:
            return name

nameMaker = NameMaker()


class QuantityNarrator:
    """ Quantity Narrator
        - Intent: to describe quantities of items in natural language
    """
    def __init__(self, items: Iterable[tuple[str, int]] = None):
        """ to INITIALIZE Quantity Narrator
            - Exported
        """
        self.items = list(items) if items is not None else []

    @staticmethod
    def pluralize(word: str) -> str:
        """ to pluralize English noun or noun phrase
            - Exported
        """
        if not word:
            return word
        words = word.split()
        if not words:
            return word
        target = words[-1]
        target_lower = target.lower()
        if target_lower.endswith(('ay', 'ey', 'iy', 'oy', 'uy')):
            plural_target = target + 's'
        elif target_lower.endswith('y') and len(target) > 1 and target_lower[-2] not in 'aeiou':
            plural_target = target[:-1] + 'ies'
        elif target_lower.endswith(('s', 'x', 'z', 'ch', 'sh')):
            plural_target = target + 'es'
        elif target_lower.endswith('is') and len(target) > 2:
            plural_target = target[:-2] + 'es'
        else:
            plural_target = target + 's'
        words[-1] = plural_target
        return ' '.join(words)

    @classmethod
    def narrateItem(cls, subject: str, quantity: int, isFirst: bool = False) -> str:
        """ to narrate single (subject, quantity) pair
            - Exported
        """
        clean_subject = subject.strip()
        if not clean_subject.isupper():
            clean_subject = clean_subject.lower()

        if quantity == 0:
            qty_word = "no"
            described = f"{qty_word} {cls.pluralize(clean_subject)}"
        elif quantity == 1:
            qty_word = "one"
            described = f"{qty_word} {clean_subject}"
        else:
            described = f"{quantity} {cls.pluralize(clean_subject)}"

        if isFirst:
            described = capName(described)
        return described

    def narrate(self_or_cls, items: Iterable[tuple[str, int]] = None) -> str:
        """ to narrate list of subject and quantity 2-tuples
            - Exported
        """
        if isinstance(self_or_cls, QuantityNarrator):
            target_items = items if items is not None else self_or_cls.items
        else:
            target_items = self_or_cls if items is None else items

        if not target_items:
            return ""
        narrated = []
        for i, (subject, qty) in enumerate(target_items):
            narrated.append(QuantityNarrator.narrateItem(subject, qty, isFirst=(i == 0)))
        return ", ".join(narrated)

    def __call__(self, items: Iterable[tuple[str, int]] = None) -> str:
        """ to narrate list of subject and quantity 2-tuples as callable
            - Exported
        """
        return self.narrate(items)

    def __str__(self) -> str:
        """ to convert Quantity Narrator to string representation
        """
        return self.narrate()


quantityNarrator = QuantityNarrator()


def narrateQuantity(items: Iterable[tuple[str, int]]) -> str:
    """ to narrate list of subject and quantity 2-tuples
        - Exported
    """
    return QuantityNarrator(items).narrate()


def upName(name: str) -> str:
    """ to capitalize all words in name leaving rest of name intact
        - Exported
    """
    return ' '.join([x[:1].upper() + x[1:] for x in name.split()])

def capName(name: str) -> str:
    """ to capitalize first words in name leaving rest of name intact
        - Exported
    """
    return name[:1].upper() + name[1:]

def unCapName(name: str) -> str:
    """ to un-capitalize first words in name leaving rest of name intact
        - Exported
    """
    return name[:1].lower() + name[1:]

def makeUnique(name: str, otherNames: Iterable[str]) -> str:
    """ to make name unique by enumeration
        - Exported
    """
    up_name = name.upper()
    serial = 0
    for candidate in otherNames:
        currentSerial = 0
        if candidate.upper().startswith(up_name):
            if len(candidate) + 3 == len(up_name):
                try:
                    currentSerial = int(candidate[-3:])
                except ValueError: continue
            elif len(name) == len(up_name):
                currentSerial = 0
            if currentSerial >= serial:
                serial = currentSerial + 1
    if serial:
        name = f'{name}{serial:03d}'
    return name

def cleanEnd(s: str) -> str:
    """ to clean end of string
        - Exported
    """
    matched = cleanEndPattern.search(s)
    if not matched: return s
    return s[:matched.start()]

def unquote(s: str) -> str:
    """ to remove excessive quote layers from string
        - Exported
    """
    s = s.strip()
    if not s: return s
    while len(s) > 1 and s[0] in ('"', "'") and s[-1] == s[0]:
        s = s[1:-1].strip()
    return s

def unbracket(s: str) -> str:
    """ to remove excessive bracket layers from string
        - Exported
    """
    if not s: return s
    for brackets in ('[]', '()', '<>'):
        if s[0] == brackets[0]:
            if s[-1] == brackets[-1]:
                return s[1:-1]
            return s[1:]
    return s

def quoteIf(s: str) -> str:
    """ to quote if
        - Exported
    """
    if ' ' not in s: return s
    if s.startswith(('"', "'")):
        if not s.endswith(s[0]):
            return s + s[0]
        return s
    s = s.replace('"', '\\"')
    return f'"{s}"'

def quote(s: str) -> str:
    """ to quote
        - Exported
    """
    if s.startswith(('"', "'")):
        if not s.endswith(s[0]):
            s = f'{s[0]}{s}{s[0]}'
    elif s.endswith(('"', "'")):
        if not s.startswith(s[0]):
            s = f'{s[-1]}{s}{s[-1]}'
    else:
        s = s.replace('"', '\\"')
        s = f'"{s}"'
    return s

def toCamel(s: str, isCapFirst: bool = True) -> str:
    """ to camel
        - Exported
    """
    for c in '_-/()[]':
        s = s.replace(c, ' ')
    s = s.strip()
    if not s: return ''
    first = s[0]
    result = ''.join(x.capitalize() for x in s.split())
    if not isCapFirst:
        result = first + result[1:]
    return result

def unCamel(s: str) -> str:
    """ to restore human name from camel notation
        - Exported
    """
    # [Esc]: quoted
    if s.startswith(('"', "'")): return s
    # [Esc]: multi-word
    if ' ' in s: return s
    result = []
    inAcronym, upperCase = False, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    for c in s:
        if c in upperCase:
            if not inAcronym:
                result.append(' ')
            inAcronym = True
        else:
            inAcronym = False
        result += c
    return ''.join(result).lstrip()

_OPERATOR_MAP = {
    '==': 'equals', '!=': 'is not', '>=': 'greater or equal', '<=': 'less or equal',
    '>': 'greater than', '<': 'less than', ' not in ': ' not in ', ' is not ': ' is not ', ' in ': ' in ', ' is ': ' is ',
}

def sanitizeProgrammaticName(text: str) -> str:
    """ to sanitize a programmatic expression for use in Nabu annotation text
        - Exported
    - Input: "raw programmatic text"
    - Output: "cleaned text"
    - Note: converts dot-notation to 'Y of X' ownership form
    - Note: un-camels identifiers
    - Note: strips all remaining punctuation (brackets, quotes, commas, etc.)
    """
    text = text.strip()
    if text.startswith('(') and text.endswith(')'):
        text = text[1:-1].strip()
    # to strip python f-string prefix
    m = re.match(r'^[fF](?:[rR]|)\s*(["\'].*)', text)
    if m:
        text = m.group(1)
    # [Scan "separator"]: to strip the long hyphen injected by the code generator and its trailing description
    for sep in (' — ', ' – ', ' - '):
        if sep in text:
            text = text.split(sep, 1)[0].strip()
    # [Opt]: to strip quotes
    text = text.replace('"', '').replace("'", '')
    # [Scan "operators"]: to replace operators before dot-handling (to avoid interference)
    for op, word in _OPERATOR_MAP.items():
        text = text.replace(op, f' {word} ')
    # [Scan "dot-notation chains"]: to convert dot-notation chains to ownership form (a.b.c -> c of b of a)
    def _dotToOwnership(match):
        parts = match.group(0).split('.')
        parts.reverse()
        return ' of '.join(parts)
    text = re.sub(r'[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+', _dotToOwnership, text)
    # [Opt]: to strip remaining punctuation and arithmetic operators
    text = re.sub(r'[.(){}\[\],;:@#$%^&*~`|\\!?=+/\-—–\']', ' ', text)
    # [Opt]: to un-camel each word
    words = text.split()
    result = ' '.join(unCamel(w) for w in words)
    # [Opt]: to collapse whitespace
    return re.sub(r'\s+', ' ', result).strip()

def makeBilingualName(name: Any, nativeName: Any, separator: str = ' ') -> str:
    """ to make bilingual name
        - Exported
    """
    name = str(name)
    if not nativeName:
        return name
    return f'{name}{separator}({nativeName})'

def concatModifiers(items: Iterable[str], sep: str = '; ') -> Optional[str]:
    """ to concatenate adjacent modifiers with separator if not null
        - Exported
    """
    result = [x for x in items if x]
    if not result: return None
    return sep.join(result)

_IRREGULAR_PLURALS = {
    'criterion': 'criteria',
    'datum': 'data',
    'medium': 'media',
    'personnel': 'personnel',
    'child': 'children',
    'man': 'men',
    'woman': 'women',
    'foot': 'feet',
    'tooth': 'teeth',
    'goose': 'geese',
    'mouse': 'mice',
}

def pluralize(word: str) -> str:
    """ to pluralize English word naturally
        - Exported
    """
    if not word:
        return ''
    lower = word.lower()
    if lower in _IRREGULAR_PLURALS:
        plural = _IRREGULAR_PLURALS[lower]
        if word.isupper():
            return plural.upper()
        if word[0].isupper():
            return plural.capitalize()
        return plural
    if lower.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return word + 'es'
    if lower.endswith('y') and len(lower) > 1 and lower[-2] not in 'aeiou':
        return word[:-1] + ('IES' if word.isupper() else ('Ies' if word[-1].isupper() else 'ies'))
    return word + ('S' if word.isupper() else 's')

def parseDocDate(dateStr: str) -> int:
    """ to parse doc date efficiently using Python facilities
        - Exported
    """
    dateStruct = None
    for fmt in ['%d-%b-%Y', '%d-%b-%y', '%d-%m-%Y', '%d-%m-%y']:
        try:
            dateStruct = time.strptime(dateStr, fmt)
            break
        except ValueError:
            pass
    if not dateStruct:
        raise ValueError(f'Invalid date {dateStr}!')
    return int(time.mktime(dateStruct))

def restoreDocDate(dateNumber: Optional[int]) -> Optional[str]:
    """ to restore doc date
        - Exported
    """
    if not dateNumber: return None
    try:
        dateStruct = time.localtime(dateNumber)
    except Exception: return None
    return time.strftime('%d-%b-%Y', dateStruct)
