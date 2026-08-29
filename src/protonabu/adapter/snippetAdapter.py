""" Module: Protonabu Snippet Adapter
    - Author: Avner Ben
        - Created: 17-May-2026
    - Generator: Antigravity (Claude Opus 4.6)
        - Generated: 17-May-2026
"""

from abc import ABC, abstractmethod
from typing import Iterator

# [Additional]
from ..factSnippet import ProtonabuSnippet


class SnippetAdapterSource(ProtonabuSnippet.ISource, ABC):
    """ Line Adapter Fact Stream
        - Purpose: to adapt Fact Line Stream (such as markdown) for foreign protonabu native format
        - Description: Wraps a concrete ISource, intercepting line-level 
          I/O to perform format-specific transformations (e.g., stripping 
          or prepending Markdown bullet decoration). Subclasses implement 
          the raw-line protocol by overriding toNative and toForeign.
    """

    def __init__(self, wrapped: ProtonabuSnippet.ISource):
        """ to INITIALIZE Line Adapter Fact Stream
            - Exported
        """
        # Contains [1:1 By Reference]: Fact Stream
        self.wrapped: ProtonabuSnippet.ISource = wrapped

    @abstractmethod
    def toNative(self, line: str) -> str:
        """ to import fact-line thru <SUBSTITUTE Line> Adapter Fact Stream
            - Exported
            - definitive [Part]
            - Input: Foreign format line
            - Output: Native format line
        """
        pass

    @abstractmethod
    def toForeign(self, line: str) -> str:
        """ to export fact-line thru <SUBSTITUTE Line> Adapter Fact Stream
            - Exported
            - Input: Native format line
            - Output: Foreign format line
        """
        pass

    def add(self, fact: str):
        """ to append line to <Line Adapter> Fact Stream
            - Exported
        """
        # [Msg]: to export fact-line thru <SUBSTITUTE Line> Adapter Fact Stream
        # [Msg]: to append line to Fact Stream
        self.wrapped.add(self.toForeign(fact))

    def __iter__(self) -> Iterator[str]:
        """ to TRAVERSE <Line Adapter> Fact Stream
            - Exported
            - definitive
        """
        # [Scan]: to TRAVERSE Fact Stream
        for line in self.wrapped:
            # [Msg]: to import fact-line thru <SUBSTITUTE Line> Adapter Fact Stream
            yield self.toNative(line)

    def close(self):
        """ to close <Line Adapter> Fact Stream
            - Exported
        """
        # [Msg]: to close Fact Stream
        self.wrapped.close()

class FactSnippetAdapter(ABC):
    """ Fact Snippet Adapter
        - Purpose: to adapt Protonabu Fact Snippet to and from foreign format
        - Stereotype: Abstract
    """
    fileExtensions: list[str] = []

    @abstractmethod
    def adaptInput(self, snippet: ProtonabuSnippet) -> ProtonabuSnippet:
        """ to import facts thru <SUBSTITUTE Fact> Snippet Adapter
            - Exported
            - Input: foreign format snippet
            - Output: native format snippet
            - definitive [Part]
        """
        pass

    @abstractmethod
    def adaptOutput(self, snippet: ProtonabuSnippet) -> ProtonabuSnippet:
        """ to export facts thru <SUBSTITUTE Fact> Snippet Adapter
            - Exported
            - Input: native format snippet
            - Output: foreign format snippet
        """
        pass
