""" Module: Educational Site Model
    - Purpose: to represent the in-memory object model of an educational site
    - Author: Avner Ben
        - Created: 14-Apr-2026
    - Generator: Antigravity (Gemini 3.5 Flash)
        - Generated: 14-Apr-2026
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


class PageElement(ABC):
    """ Page Element
        - Intent: Abstract base for all typed content elements on a foil page
    """

    @abstractmethod
    def renderHtml(self) -> str:
        """ to render <SUBSTITUTE> Page Element to HTML
            - definitive [Part]
        """
        pass

class ElementContainer(ABC):
    """ Element Container
        - Intent: Abstract base for containers holding foil page elements
    """

    @abstractmethod
    def addElement(self, element: PageElement):
        """ to add Page Element to <SUBSTITUTE Element Container>
            - definitive [Part]
        """
        pass


class HeaderElement(PageElement):
    """ Header Page Element
        - Intent: to represent a section-heading line on a foil page
    """

    def __init__(self, text: str):
        """ to INITIALIZE Header Page Element
        """
        self.text: str = text

    def renderHtml(self) -> str:
        """ to render <Header> Page Element to HTML
            - definitive [Part]
        """
        return f'<h3 class="foil-header">{self.text}</h3>\n'


class TextElement(PageElement):
    """ Text Page Element
        - Intent: to represent a plain paragraph of body text on a foil page
    """

    def __init__(self, text: str):
        """ to INITIALIZE Text Page Element
        """
        self.text: str = text

    def renderHtml(self) -> str:
        """ to render <Text> Page Element to HTML
            - definitive [Part]
        """
        return f'<p class="foil-text">{self.text}</p>\n'


class EmphasizedElement(PageElement):
    """ Emphasized Page Element
        - Intent: to represent an emphasized (bold/italic) paragraph on a foil page
    """

    def __init__(self, text: str):
        """ to INITIALIZE Emphasized Page Element
        """
        self.text: str = text

    def renderHtml(self) -> str:
        """ to render <Emphasized> Page Element to HTML
            - definitive [Part]
        """
        return f'<p class="foil-emphasized"><em>{self.text}</em></p>\n'


class CodeElement(PageElement):
    """ Code Page Element
        - Intent: to represent a preformatted code block on a foil page
    """

    def __init__(self, text: str):
        """ to INITIALIZE Code Page Element
        """
        self.text: str = text

    def renderHtml(self) -> str:
        """ to render <Code> Page Element to HTML
            - definitive [Part]
        """
        return f'<pre class="foil-code"><code>{self.text}</code></pre>\n'


class CaptionLabelElement(PageElement):
    """ Caption Label Page Element
        - Intent: to represent a descriptive side-label (e.g. "Discussion:", "Note:") on a foil page
    """

    def __init__(self, text: str):
        """ to INITIALIZE Caption Label Page Element
        """
        self.text: str = text

    def renderHtml(self) -> str:
        """ to render <Caption Label> Page Element to HTML
            - definitive [Part]
        """
        return f'<p class="foil-caption-label"><i>{self.text}</i></p>\n'


class ImageElement(PageElement):
    """ Image Page Element
        - Intent: to represent an image embedded in a foil page
    """

    def __init__(self, fileName: str, altText: str = ''):
        """ to INITIALIZE Image Page Element
        """
        self.fileName: str = fileName
        self.altText: str = altText

    def renderHtml(self) -> str:
        """ to render <Image> Page Element to HTML
            - definitive [Part]
        """
        return f'<figure class="foil-image"><img src="{self.fileName}" alt="{self.altText}"></figure>\n'


class RowElement(PageElement):
    """ Row Page Element
        - Intent: to represent a horizontal container of cells using CSS Flexbox
    """

    def __init__(self):
        """ to INITIALIZE Row Page Element
        """
        # Contains [1:0-N By Value]: Cell Element
        self.cells: list['CellElement'] = []

    def addCell(self, cell: 'CellElement'):
        """ to add Cell to Row
        """
        self.cells.append(cell)

    def renderHtml(self) -> str:
        """ to render <Row> Page Element to HTML
        """
        htmlChunks = ['<div class="foil-row">\n']
        # [Scan]: to render Page Element to HTML
        # - Giving [to append]: HTML Chunks
        for cell in self.cells:
            htmlChunks.append(cell.renderHtml())
        htmlChunks.append('</div>\n')
        return ''.join(htmlChunks)


class CellElement(PageElement, ElementContainer):
    """ Cell Page Element
        - Intent: to represent a columnar block inside a Row
    """

    def __init__(self):
        """ to INITIALIZE Cell Page Element
        """
        # Contains [1:0-N By Value]: Page Element
        self.elements: list[PageElement] = []

    def addElement(self, element: PageElement):
        """ to add Page Element to <Cell Page Element>
        """
        self.elements.append(element)

    def renderHtml(self) -> str:
        """ to render <Cell> Page Element to HTML
            - definitive [Part]
        """
        htmlChunks = ['<div class="foil-cell">\n']
        # [Scan]: to render Page Element to HTML
        # - Giving [to append]: HTML Chunks
        for element in self.elements:
            htmlChunks.append(element.renderHtml())
        htmlChunks.append('</div>\n')
        return ''.join(htmlChunks)


@dataclass
class KeywordRef:
    """ Keyword Reference
        - Intent: to tag a keyword appearing on a page for cross-referencing
        - Note: reference type may be Defined / Syntax / Explained / Referenced
    """
    keyword: str
    # - Property: reference type (Defined / Syntax / Explained / Referenced)
    refType: str


class ContinuationPage(ElementContainer):
    """ Continuation Page
        - Intent: to represent an overflow page appended to a foil page (lettered A, B, ...)
    """
    # - Property [Informative]: continuation letter sequence
    contLetters: str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def __init__(self, letter: str):
        """ to INITIALIZE Continuation Page
            - Input: continuation letter
        """
        self.letter: str = letter
        # Contains [1:0-N By Value]: Page Element [Role "content"]
        self.elements: list[PageElement] = []
        # Contains [1:0-N By Value]: Keyword Reference [Role "keywords for cross-reference"]
        self.keywords: list['KeywordRef'] = []

    def addElement(self, element: PageElement):
        """ to add Page Element to <Continuation Page>
            - definitive [Part]
            - Input: Page Element
        """        
        self.elements.append(element)

    def addKeywordRef(self, keywordRef: KeywordRef):
        """ to add Keyword Reference to Continuation Page
            - Input: Keyword Reference
        """
        self.keywords.append(keywordRef)


class Page(ElementContainer):
    """ Foil Page
        - Intent: to represent a single numbered foil in a section
    """

    def __init__(self, title: str, caption: str = '', prefix: str = ''):
        """ to INITIALIZE Foil Page
            - Input: title
            - Input [opt]: caption
            - Input : prefix
        """
        self.title: str = title
        self.caption: str = caption
        self.prefix: str = prefix
        self.num: int = 0
        # Contains [1:0-N By Value]: Page Element [Role "content"]
        self.elements: list[PageElement] = []
        # Contains [1:0-N By Value]: Continuation Page
        self.continuations: list[ContinuationPage] = []
        # Contains [1:0-N By Value]: Keyword Reference [Role "keywords"]
        self.keywords: list[KeywordRef] = []

    def addElement(self, element: PageElement):
        """ to add Page Element to <Foil Page>
            - Input: Page Element
            - definitive [Part]
        """
        self.elements.append(element)

    def addContinuation(self) -> ContinuationPage:
        """ to add Continuation Page to Foil Page
        """
        # to calculate next letter for Continuation Page
        letter = ContinuationPage.contLetters[len(self.continuations)]
        # to INITIALIZE Continuation Page
        cont = ContinuationPage(letter)
        self.continuations.append(cont)
        return cont

    def addKeyword(self, keyword: str, refType: str):
        """ to tag keyword on Foil Page for cross-reference
            - Input: keyword
            - Input: refType
        """
        self.keywords.append(KeywordRef(keyword, refType))

    @property
    def hasContinuation(self) -> bool:
        """ to tell whether Foil Page has continuation pages
        """
        return bool(self.continuations)

    @property
    def numContinuations(self) -> int:
        """ to tell the number of Continuation Pages
        """
        return len(self.continuations)

class Section:
    """ Section
        - Intent: to represent a section within a chapter, containing a sequence of foil pages
    """

    def __init__(self, title: str, descriptor: str = '', prefix: str = ''):
        """ to INITIALIZE Section
            - Input: title
            - Input [opt]: descriptor
            - Input [opt]: prefix
        """
        self.title: str = title
        self.descriptor: str = descriptor
        self.prefix: str = prefix
        self.num: int = 0
        # Contains [1:0-N By Value]: Foil Page [Role "foil pages"]
        self.pages: list[Page] = []
        self.isCrossReferenced: bool = False

    def addPage(self, page: Page) -> Page:
        """ to add Foil Page to Section
            - Input: Foil Page
            - Output: added Foil Page
            - definitive [Part]
        """
        # to set foil page number
        page.num = len(self.pages) + 1
        self.pages.append(page)
        return page

    @property
    def numPages(self) -> int:
        """ to tell the number of Foil Pages in Section
        """
        return len(self.pages)

    def collectKeywords(self) -> dict[str, dict[str, list]]:
        """ to collect keyword references across Section including continuations
            - definitive
            - Output: "keyword references index"
                - Contains: "keyword"
                - Contains: "reference type"
                - Contains: "page number"
                - IMPLEMENTATION [MAPPING]: "keywordReferencesIndex"
                    - CONTAINS [str]: "keyword"
                    - CONTAINS [MAPPING]: "referencesByType"
                        - CONTAINS [str]: "reference type"
                        - CONTAINS [list]: "page numbers"
        """
        index: dict[str, dict[str, list]] = {}
        # [Scan]: to collect keyword references
        for page in self.pages:
            allPages = [page] + list(page.continuations)
            # [Scan]: to process page and continuation pages
            for p in allPages:
                pageNum = page.num if isinstance(p, Page) else f'{page.num}{p.letter}'
                # [Scan]: to index page keywords
                for kwRef in p.keywords:
                    kw = kwRef.keyword.capitalize()
                    # [Opt]: to setup keyword entry
                    if kw not in index:
                        index[kw] = {}
                    # [Opt]: to setup reference type entry
                    if kwRef.refType not in index[kw]:
                        index[kw][kwRef.refType] = []
                    # [Opt]: to record page number in reference list
                    if pageNum not in index[kw][kwRef.refType]:
                        index[kw][kwRef.refType].append(pageNum)
        return index


class Chapter:
    """ Chapter
        - Intent: to represent a chapter in the educational site book
    """

    def __init__(self, title: str, descriptor: str = '', prefix: str = ''):
        """ to INITIALIZE Chapter
            - Input: title
            - Input [opt]: descriptor
            - Input [opt]: prefix
        """
        self.title: str = title
        self.descriptor: str = descriptor
        self.prefix: str = prefix
        # to setup chapter number within book
        # - Note: to be assigned by Book
        self.num: int = 0
        # Contains [1:0-N By Value]: Section [Role "sections"]
        self.sections: list[Section] = []

    def addSection(self, section: Section) -> Section:
        """ to add Section to Chapter
            - Input: Section
            - Output: added Section
            - definitive [Part]
        """
        # to set section number within book
        section.num = len(self.sections) + 1
        # to add Section to Chapter
        self.sections.append(section)
        return section

    @property
    def numSections(self) -> int:
        """ to tell the number of Sections in Chapter
        """
        return len(self.sections)


class Book:
    """ Book
        - Intent: to represent the top-level educational site
    """

    def __init__(self, title: str, author: str = '', version: str = ''):
        """ to INITIALIZE Book
            - Input: title
            - Input [opt]: author
            - Input [opt]: version
        """
        self.title: str = title
        self.author: str = author
        self.version: str = version
        self.date: str = ''
        self.logo: str = ''
        # Contains [1:0-N By Value]: Chapter [Role "chapters"]
        self.chapters: list[Chapter] = []

    def addChapter(self, chapter: Chapter) -> Chapter:
        """ to add Chapter to Book
            - Input: Chapter
            - Output: added Chapter
            - definitive [Part]
        """
        # to set chapter number
        chapter.num = len(self.chapters) + 1
        # to add Chapter to Book
        self.chapters.append(chapter)
        return chapter

    @property
    def numChapters(self) -> int:
        """ to tell the number of Chapters in Book
        """
        return len(self.chapters)
