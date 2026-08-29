""" Module: Markdown Snippet Adapter
    - Author: Avner Ben
        - Created: 17-May-2026
    - Generator: Antigravity (Claude Opus 4.6)
        - Generated: 17-May-2026
"""

import re

# [Additional]
from ....factSnippet import ProtonabuSnippet
# [Additional]
from ...snippetAdapter import FactSnippetAdapter, SnippetAdapterSource


# Pattern to match Markdown bullet list item prefix: "- " or "* "
_BULLET_PREFIX = re.compile(r'^(\s*)[*\-]\s')


class MarkdownAdapterSource(SnippetAdapterSource):
    """ Markdown Adapter Fact Stream
        - Purpose: to adapt Fact Stream for Markdown bullet list format
        - Description: On input, strips Markdown bullet prefixes (- or *)
        preserving indentation. On output, prepends Markdown bullet
        prefix (- ) to each line.
    """

    def toNative(self, line: str) -> str:
        """ to import fact-line thru <Markdown> Adapter Fact Stream
            - Input: Markdown line
            - Output: Native fact-line
            - definitive [Part]
        """
        line = line.rstrip('\n').rstrip('\r')
        match = _BULLET_PREFIX.match(line)
        # [Opt]: to strip Markdown bullet prefix
        if match:
            line = match.group(1) + line[match.end():]
        return line

    def toForeign(self, line: str) -> str:
        """ to export fact-line thru <Markdown> Adapter Fact Stream
            - Input: Native fact-line
            - Output: Markdown fact-line
        """
        # [Esc]: blank line
        if not line.strip():
            return line
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]
        return f'{indent}- {stripped}'


class MarkdownSnippetAdapter(FactSnippetAdapter):
    """ Markdown Snippet Adapter
        - Purpose: to adapt Protonabu Fact Snippet for Markdown bullet list format
        - Description: Converts between standard Nabu fact syntax and
        Markdown bullet list format by wrapping the snippet source
        in a MarkdownAdapterSource.
    """
    fileExtensions = ['.md']

    def adaptInput(self, snippet: ProtonabuSnippet) -> ProtonabuSnippet:
        """ to import facts thru <Markdown> Snippet Adapter
            - Exported: Markdown
            - Input: Markdown snippet
            - Output: Native format snippet
            - definitive [Part]
        """
        # [Msg]: to INITIALIZE Protonabu Snippet
        # - Using: to INITIALIZE Snippet Adapter Source
        #   - Using: snippet source
        adapted = ProtonabuSnippet(
            MarkdownAdapterSource(snippet.source),
            snippet.fileName,
            snippet.isImporting
        )
        return adapted

    def adaptOutput(self, snippet: ProtonabuSnippet) -> ProtonabuSnippet:
        """ to export facts thru <Markdown> Snippet Adapter
            - Exported: Markdown
            - Input: Native format snippet
            - Output: Markdown format snippet
        """
        # [Msg]: to INITIALIZE Protonabu Snippet
        # - Using: to INITIALIZE Snippet Adapter Source
        #   - Using: snippet source
        adapted = ProtonabuSnippet(
            MarkdownAdapterSource(snippet.source),
            snippet.fileName,
            snippet.isImporting
        )
        return adapted
