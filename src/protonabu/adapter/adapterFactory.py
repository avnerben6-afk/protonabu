""" Module: Protonabu Snippet Adapter Factory
    - Author: Avner Ben
        - Created: 17-May-2026
    - Generator: Antigravity (Claude Opus 4.6)
        - Generated: 17-May-2026
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from ..util.error import InternalError
# [Additional]
if TYPE_CHECKING:
    from ..factSnippet import ProtonabuSnippet
# [Additional]
from .snippetAdapter import FactSnippetAdapter


class SnippetAdapterFactory:
    """ Snippet Adapter Factory
        - Purpose: to provide Snippet Adapter by file extension
        - Stereotype: Singleton
    """

    def __init__(self):
        """ to INITIALIZE Snippet Adapter Factory
            - Exported
        """
        # Contains [0-N by Reference]: Snippet Adapter [Role "adapters]
        # - Key: file extension
        self.adapters: dict[str, FactSnippetAdapter] = {}

    def register(self, adapter: FactSnippetAdapter):
        """ to register Snippet Adapter
            - Exported
            - definitive [Part]
        """
        # [Scan "file extensions"]: to register adapter
        for ext in adapter.fileExtensions:
            normalizedExt = ext if ext.startswith('.') else f'.{ext}'
            # [Esc "Error"]: duplicate registration
            if normalizedExt in self.adapters:
                raise InternalError('Snippet adapter already registered for extension', [
                    ('Extension', normalizedExt),
                    ('Existing', type(self.adapters[normalizedExt]).__name__),
                    ('New', type(adapter).__name__)
                ])
            self.adapters[normalizedExt] = adapter

    def getAdapter(self, fileName: str) -> Optional[FactSnippetAdapter]:
        """ to get Snippet Adapter by file name
            - Exported
            - Output [Opt None]: Snippet Adapter
        """
        ext = Path(fileName).suffix.lower()
        return self.adapters.get(ext)

    def hasAdapter(self, fileName: str) -> bool:
        """ to tell if Snippet Adapter is registered for file name
            - Exported
        """
        ext = Path(fileName).suffix.lower()
        return ext in self.adapters

    def adaptInput(self, 
        snippet: ProtonabuSnippet
    ) -> ProtonabuSnippet:
        """ to adapt snippet input using registered adapter
            - Exported
            - Input: raw snippet
            - Output: native snippet
            - definitive [Product]
        """
        # [Msg]: to get Snippet Adapter by file name
        adapter = self.getAdapter(snippet.fileName)
        # [Esc Done]: no adapter registered
        if not adapter: return snippet
        # [Msg]: to adapt snippet input from foreign format
        return adapter.adaptInput(snippet)

    def adaptOutput(self,
        snippet: ProtonabuSnippet
    ) -> ProtonabuSnippet:
        """ to adapt snippet output using registered adapter
            - Exported
            - Input: nativesnippet
            - Output: adapted snippet
        """
        # [Msg]: to get Snippet Adapter by file name
        adapter = self.getAdapter(snippet.fileName)
        # [Esc Done]: no adapter registered
        if not adapter: return snippet
        # [Msg]: to adapt snippet output to foreign format
        return adapter.adaptOutput(snippet)


# to INITIALIZE Snippet Adapter Factory
snippetAdapterFactory = SnippetAdapterFactory()
