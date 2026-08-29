""" Package: Protonabu Snippet Adapter
    - Author: Avner Ben
        - Created: 17-May-2026
    - Generator: Antigravity (Claude Opus 4.6)
        - Generated: 17-May-2026
"""

from .adapterFactory import snippetAdapterFactory

# to register standard Snippet Adapters
from .std.MarkdownSnippetAdapter.markdownSnippetAdapter import MarkdownSnippetAdapter
from .std.JsonSnippetAdapter.jsonSnippetAdapter import JsonSnippetAdapter
from .std.XmlSnippetAdapter.xmlSnippetAdapter import XmlSnippetAdapter

snippetAdapterFactory.register(MarkdownSnippetAdapter())
snippetAdapterFactory.register(JsonSnippetAdapter())
snippetAdapterFactory.register(XmlSnippetAdapter())

