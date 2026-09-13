""" Module: Protonabu String Utilities
    - Author: Avner Ben
        - Created: 1-Oct-2005
        - Improved: 1-Jan-2024
        - Improved: 28-Aug-2026
            - Moved here from the Nabu project
        - Improved: 30-Aug-2026
            - Clean synthetic in-code annotations
        - Improved: 13-Sep-2026
            - Added suggestSimilar method to NameMaker with RapidFuzz and difflib fallback
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
        """ to INITIALIZE ID Counter
            - Input [Opt "group"]: prefix
            - Input [Opt "0"]: start
        """
        self.start = start
        self.counter = start
        self.prefix = prefix
        IdCounter._instances.append(self)
        
    def next(self)-> str:
        """ to get next ID
            - Output: result
        """
        self.counter += 1
        return f'{self.prefix}_{self.counter}'

    @classmethod
    def resetAll(cls):
        """ to reset all initialized ID Counters across modules
            - Input: cls
        """
        # [Scan "Instance"]: to reset ID Counter to start value
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
            - Input: cls
        """
        cls._magic_methods = dict(mapping)

    @property
    def MAGIC_METHODS(self) -> dict[str, str]:
        """ to get magic methods mapping
            - Output: result
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
            - Input: kwd
            - Input [Opt "True"]: add To Abbrevs
            - Input [Opt "True"]: add To Cross Abbrevs
        """
        kwd, abbrev = kwd.strip().capitalize(), abbrev.strip().capitalize()
        # [Opt]: to set abbreviation in Name Maker 
        if addToAbbrevs:
            self.abbrevs[kwd] = abbrev
        # [Opt]: to set cross-abbreviation in Name maker
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
            - Input: name
            - Input [Opt ""]: suffix
            - Input [Opt ""]: ignore Last
            - Input [Opt "True"]: cap First
            - Input [Opt "False"]: is Acronym
            - Output: result
        """
        # [Esc Error]: Missing name
        if not name:
            raise InternalError('Missing name')
        # [Guard]: to look up suffix abbreviation
        try: 
            suffix = self.abbrevs[suffix]
        # [Esc]: not in abbreviations
        except KeyError: 
            pass
        words, curW = [], ''
        ignoreLast = ignoreLast.upper()
        # [Opt "All Uppercase"]: to convert name to lowercase
        if name.isupper():
            name = name.lower()
        # [Scan "Character"]: to separate words by delimiters and letter case
        for c in name:
            ordC = ord(c)
            # [Opt "Delimiter"]: to complete current word at word boundary
            if c in self.delims:
                if curW:
                    words.append(curW)
                    curW = ''
            # [Alt "Uppercase or Digit"]: to start new word on capital letter or digit
            elif self.stUp <= ordC <= self.endUp or self.stNum <= ordC <= self.endNum:
                if curW:
                    words.append(curW)
                curW = c
            # [Alt "Lowercase Letter"]: to append character to current word
            elif self.stLow <= ordC <= self.endLow:
                curW += c
            # [Alt "Other Character"]: to flush current accumulated word
            elif curW:
                words.append(curW)
                curW = ''
        # [Opt "Remaining Word"]: to append final accumulated word
        if curW:
            words.append(curW)
        # [Opt "Ignored Trailing Word"]: to remove specified trailing word
        if words and words[-1].upper() == ignoreLast:
            words.remove(words[-1])
        # [Opt]: to remove trailing articles and prepositions
        trailing_to_strip = {'to', 'the', 'a', 'an', 'of', 'at', 'by', 'in', 'on', 'with', 'for', 'from'}
        # [Rpt]: to strip trailing articles and prepositions
        while words and words[-1].lower() in trailing_to_strip:
            words.pop()
        # [Scan; Opt]: to filter out embedded articles
        filtered_words = [w for w in words if w.lower() not in ('to', 'the', 'a', 'an')]
        # [Opt "Filtered Words Available"]: to use filtered words list
        if filtered_words:
            words = filtered_words
        # [Esc Error]: cannot make programmatic name
        if not words:
            raise Error(f'cannot make programmatic name for "{name}"')
        # [Opt]: to leave name unabbreviated
        # - Reason: single word name
        if len(words) == 1:
            # [Opt "Capitalize First"]: to capitalize single word
            if capFirst: result = words[0][0].upper() + words[0][1:]
            # [Alt "Lowercase First"]: to lowercase single word
            else: result = words[0][0].lower() + words[0][1:]
        # [Alt]: to concatenate capitalized words in name
        else:
            result, start = '', 1
            # [Scan "Word"]: to abbreviate and concatenate words
            for word in words:
                # [Opt "First Word or Capitalize"]: to capitalize initial word
                if capFirst or not start:
                    preAbbrev = word.capitalize()
                # [Alt "Subsequent Word"]: to lowercase subsequent word
                else:
                    preAbbrev = word.lower()
                start = 0
                # [Opt "Registered Abbreviation"]: to substitute word with registered abbreviation
                if preAbbrev in self.abbrevs:
                    result += self.abbrevs[preAbbrev]
                # [Alt "Capitalized Registered Abbreviation"]: to substitute lowercased abbreviation
                elif (upPreAbbrev := preAbbrev[0].upper() + preAbbrev[1:]) in self.abbrevs:
                    result += self.abbrevs[upPreAbbrev].lower()
                # [Alt "Unregistered Word"]: to append word unchanged
                else:
                    result += preAbbrev
            # [Opt]: to make acronym of name
            if len(result) > 32 and isAcronym:
                result = ''
                for word in words:
                    result += word[0].upper()
        # [Opt "Suffix Provided"]: to append programmatic suffix
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
        # [Msg]: to make programmatic name from literate name
        base_name = self.makeProgrammaticName(
            name,
            suffix=suffix,
            ignoreLast=ignoreLast,
            capFirst=capFirst,
            isAcronym=isAcronym
        )
        # [Esc]: no scopes provided
        if not scopes:
            return base_name
            
        # [Opt "Single Scope"]: to wrap scope in list
        if not isinstance(scopes, (list, tuple)):
            scopes = [scopes]
            
        unique_name = base_name
        counter = 1
        # [Rpt]: to find unique programmatic name by enumeration
        while True:
            collision = False
            # [Scan "Scope"]: to check for name collision in scope registry
            for scope in scopes:
                # [Opt "Registered Scope"]: to inspect scope namespace for collision
                if scope is not None and scope in self._registries:
                    if unique_name in self._registries[scope]:
                        existing_ref = self._registries[scope][unique_name]
                        # [Opt "Different Reference"]: to flag name collision
                        if ref is None or existing_ref is None or existing_ref is not ref:
                            collision = True
                            break
            # [Esc Done]: no collision detected
            if not collision:
                break
            unique_name = f"{base_name}{counter}"
            counter += 1
            
        # [Scan "Scope"]: to record unique name in scope registries
        for scope in scopes:
            # [Opt "Valid Scope"]: to register unique name with reference
            if scope is not None:
                if scope not in self._registries:
                    self._registries[scope] = {}
                self._registries[scope][unique_name] = ref
                
        return unique_name

    def register(self, name: str, scopes: list, ref: Any = None):
        """ to register an existing name in the given scopes
            - Exported
            - Input: name
            - Input [Opt "None"]: ref
        """
        # [Esc]: not scopes
        if not scopes:
            return
        # [Opt "Single Scope"]: to wrap scope in list
        if not isinstance(scopes, (list, tuple)):
            scopes = [scopes]
        # [Scan "Scope"]: to register name across scopes
        for scope in scopes:
            # [Opt "Valid Scope"]: to store name in scope registry
            if scope is not None:
                if scope not in self._registries:
                    self._registries[scope] = {}
                self._registries[scope][name] = ref

    def clearRegistries(self):
        """ to clear all registries
            - Exported
        """
        self._registries.clear()

    def suggestSimilar(
        self,
        name: str,
        scope: Any = None,
        limit: int = 3,
        cutoff: float = 0.6
    ) -> list[str]:
        """ to suggest similar names from scope registry
            - Exported
            - Input: name
            - Input [Opt "None"]: scope
            - Input [Opt "3"]: limit
            - Input [Opt "0.6"]: cutoff
            - Output: candidate names
        """
        # [Esc]: empty name
        if not name:
            return []

        # to collect candidate pool from target registry or all registries
        candidates: set[str] = set()
        if scope is not None:
            if scope in self._registries:
                candidates.update(self._registries[scope].keys())
        else:
            for reg in self._registries.values():
                candidates.update(reg.keys())

        # [Esc]: no candidates in scope
        if not candidates:
            return []

        # [Guard]: to try RapidFuzz fuzzy candidate matching
        try:
            from rapidfuzz import process, fuzz
            matches = process.extract(
                name,
                candidates,
                scorer=fuzz.ratio,
                limit=limit,
                score_cutoff=cutoff * 100.0
            )
            return [m[0] for m in matches]
        # [Esc Error]: RapidFuzz not installed, fallback to difflib
        except ImportError:
            import difflib
            return difflib.get_close_matches(name, list(candidates), n=limit, cutoff=cutoff)

    def unMakeProgrammaticName(
            self,
            s: str,
            suffix=None,
            lowerCaseAbbreviations=False,
            upper=False
    ) -> str:
        """ to restore literate name from programmatic name
            - Exported
            - Input: s
            - Input [Opt "None"]: suffix
            - Input [Opt "False"]: lower Case Abbreviations
            - Input [Opt "False"]: upper
            - Output: result
        """
        # [Esc]: not s
        if not s: return s
        # [Opt "Upper"]: to capitalize initial character
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
            # [Alt]: to separate name at underscore
            elif c in ["_"]:
                if i > startPos:
                    parts.append(s[startPos:i])
                startPos = i + 1
        # [Opt]: to separate last name
        if startPos < len(s):
            parts.append(s[startPos:])
        # [Opt "Missing Suffix"]: to append suffix
        if suffix and parts[-1].upper() != suffix.upper():
            parts.append(suffix)
        # [Scan; Opt]: to filter out empty name segments
        parts = [x.strip() for x in parts if x.strip()]
        # [Scan "Segment"]: to expand abbreviations to literate words
        for i, part in enumerate(parts):
            try:
                part = self.crossAbbrevs[part.capitalize()]
                if lowerCaseAbbreviations:
                    part = part[0].lower() + part[1:]
                parts[i] = part
            # [Esc Error]: "KeyError"
            except KeyError: pass
        result = ' '.join(parts)
        return result

    def translateMagicMethod(self, methodName: str) -> str:
        """ to translate magic method to Nabu capability verb
            - Exported
            - Input: method Name
            - Output: result
        """
        # [Esc]: method Name in self MAGIC_ METHODS
        if methodName in self.MAGIC_METHODS:
            return self.MAGIC_METHODS[methodName]
        verb = unCamel(methodName).lower().replace('_', ' ')
        return ' '.join(verb.split())

    def processWord(self, name: str) -> str:
        """ to programmatize name
            - Exported
            - Input: name
            - Output: result
        """
        # [Esc]: in name
        if ' ' in name:
            return self.makeProgrammaticName(name)
        # [Guard]: to look up abbreviation for single word
        try:
            return self.abbrevs[name.capitalize()]
        # [Esc Error]: "KeyError"
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
            - Input [Opt "None"]: items
        """
        self.items = list(items) if items is not None else []

    @staticmethod
    def pluralize(word: str) -> str:
        """ to pluralize English noun or noun phrase
            - Exported
            - Input: word
            - Output: result
        """
        # [Esc]: not word
        if not word:
            return word
        words = word.split()
        # [Esc]: not words
        if not words:
            return word
        target = words[-1]
        target_lower = target.lower()
        # [Opt "Vowel Before Y"]: to append s to target word
        if target_lower.endswith(('ay', 'ey', 'iy', 'oy', 'uy')):
            plural_target = target + 's'
        # [Alt "Consonant Before Y"]: to replace trailing y with ies
        elif target_lower.endswith('y') and len(target) > 1 and target_lower[-2] not in 'aeiou':
            plural_target = target[:-1] + 'ies'
        # [Alt "Sibilant Ending"]: to append es to target word
        elif target_lower.endswith(('s', 'x', 'z', 'ch', 'sh')):
            plural_target = target + 'es'
        # [Alt "Latin IS Ending"]: to replace trailing is with es
        elif target_lower.endswith('is') and len(target) > 2:
            plural_target = target[:-2] + 'es'
        # [Alt "Regular Ending"]: to append standard s plural suffix
        else:
            plural_target = target + 's'
        words[-1] = plural_target
        return ' '.join(words)

    @classmethod
    def narrateItem(cls, subject: str, quantity: int, isFirst: bool = False) -> str:
        """ to narrate item
            - Exported
            - Input: cls
            - Input [Opt "False"]: is First
            - Output: result
        """
        clean_subject = subject.strip()
        # [Opt "Mixed Case"]: to lowercase subject noun
        if not clean_subject.isupper():
            clean_subject = clean_subject.lower()

        # [Opt "Zero Quantity"]: to narrate zero items as no <plural>
        if quantity == 0:
            qty_word = "no"
            described = f"{qty_word} {cls.pluralize(clean_subject)}"
        # [Alt "Single Item"]: to narrate single item as one <singular>
        elif quantity == 1:
            qty_word = "one"
            described = f"{qty_word} {clean_subject}"
        # [Alt "Multiple Items"]: to narrate count with pluralized subject
        else:
            described = f"{quantity} {cls.pluralize(clean_subject)}"

        # [Opt]: to capitalize first words in name leaving rest of name intact
        if isFirst:
            described = capName(described)
        return described

    def narrate(self_or_cls, items: Iterable[tuple[str, int]] = None) -> str:
        """ to narrate list of subject and quantity 2-tuples
            - Exported
            - Input: self_or_cls
            - Input [Opt "None"]: items
            - Output: result
        """
        # [Opt]: to decide target_items
        if isinstance(self_or_cls, QuantityNarrator):
            target_items = items if items is not None else self_or_cls.items
        # [Alt]: to decide target_items
        else:
            target_items = self_or_cls if items is None else items

        # [Esc]: not target_items
        if not target_items:
            return ""
        narrated = []
        # [Scan "Item"]: to narrate each subject and quantity pair
        for i, (subject, qty) in enumerate(target_items):
            narrated.append(QuantityNarrator.narrateItem(subject, qty, isFirst=(i == 0)))
        return ", ".join(narrated)

    def __call__(self, items: Iterable[tuple[str, int]] = None) -> str:
        """ to narrate list of subject and quantity 2-tuples as callable
            - Exported
            - Input [Opt "None"]: items
            - Output: result
        """
        # [Msg]: to narrate list of subject and quantity 2-tuples
        return self.narrate(items)

    def __str__(self) -> str:
        """ to convert Quantity Narrator to string representation
            - Output: result
        """
        # [Msg]: to narrate list of subject and quantity 2-tuples
        return self.narrate()


quantityNarrator = QuantityNarrator()


def narrateQuantity(items: Iterable[tuple[str, int]]) -> str:
    """ to narrate list of subject and quantity 2-tuples
        - Exported
        - Input: items
        - Output: result
    """
    return QuantityNarrator(items).narrate()


def upName(name: str) -> str:
    """ to capitalize all words in name leaving rest of name intact
        - Exported
        - Input: name
        - Output: result
    """
    return ' '.join([x[:1].upper() + x[1:] for x in name.split()])

def capName(name: str) -> str:
    """ to capitalize first words in name leaving rest of name intact
        - Exported
        - Input: name
        - Output: result
    """
    return name[:1].upper() + name[1:]

def unCapName(name: str) -> str:
    """ to un-capitalize first words in name leaving rest of name intact
        - Exported
        - Input: name
        - Output: result
    """
    return name[:1].lower() + name[1:]

def makeUnique(name: str, otherNames: Iterable[str]) -> str:
    """ to make name unique by enumeration
        - Exported
        - Input: name
        - Input: other Names
        - Output: result
    """
    up_name = name.upper()
    serial = 0
    # [Scan "Candidate"]: to find highest existing serial suffix
    for candidate in otherNames:
        currentSerial = 0
        if candidate.upper().startswith(up_name):
            # [Opt "Matching Length"]: to parse serial suffix from candidate
            if len(candidate) + 3 == len(up_name):
                # [Guard]: to parse 3-digit serial number
                try:
                    currentSerial = int(candidate[-3:])
                # [Esc Error]: "ValueError"
                except ValueError: continue
            # [Alt "Exact Name Match"]: to reset current serial to zero
            elif len(name) == len(up_name):
                currentSerial = 0
            # [Opt "Higher Serial Found"]: to increment next serial number
            if currentSerial >= serial:
                serial = currentSerial + 1
    # [Opt "Serial Suffix Required"]: to append 3-digit serial suffix to name
    if serial:
        name = f'{name}{serial:03d}'
    return name

def cleanEnd(s: str) -> str:
    """ to clean end of string
        - Exported
        - Input: s
        - Output: result
    """
    matched = cleanEndPattern.search(s)
    # [Esc]: not matched
    if not matched: return s
    return s[:matched.start()]

def unquote(s: str) -> str:
    """ to remove excessive quote layers from string
        - Exported
        - Input: s
        - Output: result
    """
    s = s.strip()
    # [Esc]: not s
    if not s: return s
    # [Rpt]: to strip matching outer quote pairs
    while len(s) > 1 and s[0] in ('"', "'") and s[-1] == s[0]:
        s = s[1:-1].strip()
    return s

def unbracket(s: str) -> str:
    """ to remove excessive bracket layers from string
        - Exported
        - Input: s
        - Output: result
    """
    # [Esc]: not s
    if not s: return s
    # [Scan "Bracket Pair"]: to strip matching outer bracket pair
    for brackets in ('[]', '()', '<>'):
        # [Esc]: s 0 equals brackets 0
        if s[0] == brackets[0]:
            if s[-1] == brackets[-1]:
                return s[1:-1]
            return s[1:]
    return s

def quoteIf(s: str) -> str:
    """ to quote if
        - Exported
        - Input: s
        - Output: result
    """
    # [Esc]: not in s
    if ' ' not in s: return s
    # [Esc]: s startswith not endswith of s s 0
    if s.startswith(('"', "'")):
        if not s.endswith(s[0]):
            return s + s[0]
        return s
    s = s.replace('"', '\"')
    return f'"{s}"'

def quote(s: str) -> str:
    """ to quote
        - Exported
        - Input: s
        - Output: result
    """
    # [Opt "Missing Closing Quote"]: to close opening quote
    if s.startswith(('"', "'")):
        if not s.endswith(s[0]):
            s = f'{s[0]}{s}{s[0]}'
    # [Alt "Missing Opening Quote"]: to match closing quote
    elif s.endswith(('"', "'")):
        if not s.startswith(s[0]):
            s = f'{s[-1]}{s}{s[-1]}'
    # [Alt "Unquoted String"]: to wrap string in escaped double quotes
    else:
        s = s.replace('"', '\"')
        s = f'"{s}"'
    return s

def toCamel(s: str, isCapFirst: bool = True) -> str:
    """ to camel
        - Exported
        - Input: s
        - Input [Opt "True"]: is Cap First
        - Output: result
    """
    # [Scan "Delimiter"]: to replace delimiters with spaces
    for c in '_-/()[]':
        s = s.replace(c, ' ')
    s = s.strip()
    # [Esc]: not s
    if not s: return ''
    first = s[0]
    result = ''.join(x.capitalize() for x in s.split())
    # [Opt "Preserve Initial Lowercase"]: to retain first letter case
    if not isCapFirst:
        result = first + result[1:]
    return result

def unCamel(s: str) -> str:
    """ to restore human name from camel notation
        - Exported
        - Input: s
        - Output: result
    """
    # [Esc]: quoted
    if s.startswith(('"', "'")): return s
    # [Esc]: multi-word
    if ' ' in s: return s
    result = []
    inAcronym, upperCase = False, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    # [Scan "Character"]: to separate camel-cased words with spaces
    for c in s:
        # [Opt "Uppercase or Digit"]: to insert space before capital letter
        if c in upperCase:
            if not inAcronym:
                result.append(' ')
            inAcronym = True
        # [Alt "Lowercase"]: to reset acronym flag
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
    # [Opt "Enclosing Parentheses"]: to strip outer parentheses
    if text.startswith('(') and text.endswith(')'):
        text = text[1:-1].strip()
    # [Msg]: to strip python f-string prefix
    m = re.match(r'^[fF](?:[rR]|)\s*(["\'].*)', text)
    # [Opt "F-String Prefix"]: to extract string content from f-string
    if m:
        text = m.group(1)
    # [Scan "separator"]: to strip the long hyphen injected by the code generator and its trailing description
    for sep in (' — ', ' – ', ' - '):
        if sep in text:
            text = text.split(sep, 1)[0].strip()
    # [Msg]: to strip quotes
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
    # [Msg]: to strip remaining punctuation and arithmetic operators
    text = re.sub(r'[.(){}\[\],;:@#$%^&*~`|\\!?=+/\-—–"\']', ' ', text)
    # [Msg]: to un-camel each word
    words = text.split()
    result = ' '.join(unCamel(w) for w in words)
    # [Opt]: to collapse whitespace
    return re.sub(r'\s+', ' ', result).strip()

def makeBilingualName(name: Any, nativeName: Any, separator: str = ' ') -> str:
    """ to make bilingual name
        - Exported
        - Input: name
        - Input: native Name
        - Input [Opt " "]: separator
        - Output: result
    """
    name = str(name)
    # [Esc]: not native Name
    if not nativeName:
        return name
    return f'{name}{separator}({nativeName})'

def concatModifiers(items: Iterable[str], sep: str = '; ') -> Optional[str]:
    """ to concatenate adjacent modifiers with separator if not null
        - Exported
        - Input: items
        - Output: result
    """
    # [Scan; Opt]: to filter non-empty modifier strings
    result = [x for x in items if x]
    # [Esc]: not result
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
        - Input: word
        - Output: result
    """
    # [Esc]: not word
    if not word:
        return ''
    lower = word.lower()
    # [Esc]: lower in _ IRREGULAR_ PLURALS
    if lower in _IRREGULAR_PLURALS:
        plural = _IRREGULAR_PLURALS[lower]
        # [Esc]: isupper of word
        if word.isupper():
            return plural.upper()
        # [Esc]: word 0 isupper
        if word[0].isupper():
            return plural.capitalize()
        return plural
    # [Esc]: lower endswith s x z ch sh
    if lower.endswith(('s', 'x', 'z', 'ch', 'sh')):
        return word + 'es'
    # [Esc]: lower endswith y and len lower greater than 1 and lower
    if lower.endswith('y') and len(lower) > 1 and lower[-2] not in 'aeiou':
        return word[:-1] + ('IES' if word.isupper() else ('Ies' if word[-1].isupper() else 'ies'))
    return word + ('S' if word.isupper() else 's')

def parseDocDate(dateStr: str) -> int:
    """ to parse doc date efficiently using Python facilities
        - Exported
        - Input: date Str
        - Output: result
    """
    dateStruct = None
    # [Scan "Date Format"]: to attempt parsing date string with standard formats
    for fmt in ['%d-%b-%Y', '%d-%b-%y', '%d-%m-%Y', '%d-%m-%y']:
        # [Guard]: to parse date string with format
        try:
            dateStruct = time.strptime(dateStr, fmt)
            break
        # [Esc Error]: "ValueError"
        except ValueError:
            pass
    # [Esc Error]: "Invalid date date Str"
    if not dateStruct:
        raise ValueError(f'Invalid date {dateStr}!')
    # [Msg]: to convert time structure to epoch timestamp
    return int(time.mktime(dateStruct))

def restoreDocDate(dateNumber: Optional[int]) -> Optional[str]:
    """ to restore doc date
        - Exported
        - Input: date Number
        - Output: result
    """
    # [Esc]: not date Number
    if not dateNumber: return None
    # [Guard]: to convert epoch timestamp to local time structure
    try:
        dateStruct = time.localtime(dateNumber)
    # [Esc]: Exception
    except Exception: return None
    return time.strftime('%d-%b-%Y', dateStruct)
