""" Module: Protonabu Loop Utilities
    - Author: Avner Ben
        - Created: 1-Jan-2020
        - Improved: 28-Aug-2026
            - Moved here from the Nabu project
        - Improved: 13-Sep-2026
            - Integrated more-itertools for sequence traversal and re-exported core iter utilities
"""

from typing import Iterable, Iterator, Callable, Any, Optional
from more_itertools import (
    first as _more_first,
    peekable,
    chunked,
    pairwise,
    one,
    partition
)

def first(anIterable: Iterable, default: Any = None) -> Optional[Any]:
    """ to retrieve first element in iterable efficiently
        - Exported
        - Input: an Iterable
        - Input [OPT "None"]: default
        - Output: result
    """
    return _more_first(anIterable, default=default)

def find(where: Iterable, cmp: Callable[[Any], bool]) -> Any:
    """ to find first occurrence in iterable
        - Exported
        - Input: where
        - Input: to compare with object
        - Output: result
    """
    # [Scan]: to compare with object
    for x in where:
        # [Esc Done]: equal
        if cmp(x): return x
    return None

def findBehind(where: Iterable, cmp: Callable[[Any], Any]) -> Any:
    """ to find first occurrence produced by iterable
        - Exported
        - Input: where
        - Input: to compare with object
        - Output: result
    """
    # [Scan]: to compare with object
    for x in where:
        # [Esc Done]: result equal
        if (result := cmp(x)): return result
    return None

def findIndex(where: Iterable, cmp: Callable[[Any], bool]) -> int:
    """ to find first occurrence position in iterable
        - Exported
        - Input: where
        - Input: to compare with object
        - Output: result
    """
    # [Scan]: to compare with object
    for i, x in enumerate(where):
        # [Esc]: equal
        if cmp(x): return i
    return -1

def findNested(
        where: Iterable, 
        getInner: Callable[[Any], Any], 
        cmp: Callable[[Any], bool]) -> Any:
    """ to find first occurrence in nested iterable
        - Exported
        - Input: where
        - Input: to get inner
        - Input: to compare with object
        - Output: result
    """
    # [Scan]: to compare objects contained
    for x in where:
        # [Esc Once]: nothing internal to iterate on
        if not (inner := getInner(x)): continue
        # [Scan]: to compare with object
        for y in inner:
            # [Esc]: equal
            if cmp(y): return y
    return None

def exists(where: Iterable, cmp: Callable[[Any], bool]) -> bool:
    """ to tell if item exists in iterable
        - Exported
        - Input: where
        - Input: to compare with object
        - Output: result
    """
    # [Scan]: to compare with object
    for x in where:
        # [Esc Done]: equal
        if cmp(x): return True
    return False

def count(where: Iterable, cmp: Callable[[Any], bool]) -> int:
    """ to count occurrences in iterable
        - Exported
        - Input: where
        - Input: to compare with object
        - Output: result
    """
    result = 0
    # [Scan; Opt"to compare with object"]: to increment count
    for x in where:
        if cmp(x): result += 1
    return result

def findNoCase(where, target: str):
    """ to find first string occurrence in iterable case-insensitive
        - Exported
        - Input: where
        - Input: target
        - Output: result
    """
    target = target.upper()
    # [Scan; Opt]: to compare with upper-cased
    for x in where:
        # [Esc Done]: found
        if x.upper() == target: return x
    # [Esc "Exhausted"]: not found
    return None

def firstValid(first: Any, second: Any):
    """ to find first True object among two
        - Exported
        - Input: first
        - Input: second
        - Output: result
    """
    return first if first else second

def iterUp(node: Any, getOwner: Callable[[Any], Any]) -> Iterator[Any]:
    """ to iterate up hierarchy that supports back-reference
        - Exported
        - Input: node
        - Input: to get owner
        - Output: owner
    """
    def walk(node: Any):
        """ to iterate up sub-hierarchy that supports back-reference
        """
        # [Msg]: to get initial owner
        owner = getOwner(node)
        # [Scan "owners"]: to iterate up sub-hierarchy
        while owner is not None:
            # [Esc]: already visited
            if owner in visited: break
            # to mark owner as visited
            visited.add(owner)
            # to PICK up owner
            yield owner
            # to progress one owner up
            node = owner
            # [Msg]: to get next owner
            owner = getOwner(node)
 
    visited: set[Any] = set()
    # [Scan]: to iterate up sub-hierarchy that supports back-reference
    yield from walk(node)

def iterUps(node: Any, getOwners: Callable[[Any], Iterator[Any]]) -> Iterator[Any]:
    """ to iterate up network hierarchy that supports back-reference
        - Exported
        - Input: node
        - Input: to EXPAND owners
        - Output: owners
    """
    def walk(node: Any):
        """ to iterate up network sub-hierarchy that supports back-reference
        """
        # [Rpt "to EXPAND owners"; Scan "owners"]: to iterate up network sub-hierarchy
        for owner in getOwners(node):
            # [Esc]: already visited
            if owner in visited: continue
            # to mark owner as visited
            visited.add(owner)
            # to PICK up owner in many
            yield owner
            # [Msg]: to iterate up network sub-hierarchy
            yield from walk(owner)

    visited: set[Any] = set()
    # [Msg]: to iterate up network sub-hierarchy that supports back-reference
    yield from walk(node)
