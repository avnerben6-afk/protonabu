""" Module: Educational Site Parser
    - Purpose: to parse an educational site Protonabu script into the site object model
    - Author: Avner Ben
        - Created: 14-Apr-2026
        - Improved: 25-Jun-2026
    - Generator: Antigravity (Gemini 3.5 Flash)
        - Generated: 14-Apr-2026
"""

import sys
from pathlib import Path
from typing import Optional

# [Additional]
from .. import (
    ProtonabuParser,
    ProtonabuParseDispatcher,
    ProtonabuSchema,
    ProtonabuSnippetFromFile,
)
from ..util.error import Error
# [Additional]
from .siteModel import (
    Book, Chapter, Section, Page, ContinuationPage, KeywordRef,
    HeaderElement, TextElement, EmphasizedElement,
    CodeElement, CaptionLabelElement, ImageElement,
    RowElement, CellElement,
    PageElement, ElementContainer,
)

_SCHEMA_PATH = Path(__file__).parent / 'schema.facts'


class SiteParser(ProtonabuParser):
    """ Educational Site Parser
        - Intent: to parse a Protonabu educational site script and build a Book object model
        - Stereotype: Composite
    """

    def __init__(self):
        """ to INITIALIZE Educational Site Parser
        """
        # [Msg]: to INITIALIZE Protonabu Schema from schema file
        schema = ProtonabuSchema(
            ProtonabuSnippetFromFile(_SCHEMA_PATH)
        )
        # [Msg]: to INITIALIZE Protonabu Tokenizer
        super().__init__(schema, _SCHEMA_PATH.parent)
        # Contains [1:0-1 By Value]: Book [Role "result"]
        self.book: Optional[Book] = None
        # Contains [1:0-1 By Reference]: Chapter [Role "current chapter"]
        self._currentChapter: Optional[Chapter] = None
        # Contains [1:0-1 By Reference]: Section [Role "current section"]
        self._currentSection: Optional[Section] = None
        # Contains [1:0-1 By Reference]: Foil Page [Role "current page"]
        self._currentPage: Optional[Page] = None
        # Contains [1:0-1 By Reference]: Continuation Page [Role "current continuation"]
        self._currentContinuation: Optional[ContinuationPage] = None
        # [Msg]: to initialize Protonabu Fact parse dispatcher
        self._dispatcher: ProtonabuParseDispatcher = self._initDispatch()

    def _initDispatch(self) -> ProtonabuParseDispatcher:
        """ to initialize Protonabu Fact parse dispatcher
        """
        # [Msg]: to INITIALIZE Protonabu Fact parse Dispatcher
        dispatcher = ProtonabuParseDispatcher()
        # [Msg]: to find and register Labeled Fact line handlers
        dispatcher.loadHandlers(self.schema.labels, self)
        return dispatcher

    # ------------------------------------------------------------------
    # Parse handlers — one per schema label
    # ------------------------------------------------------------------

    def parseBook(self, fact) -> Book:
        """ to parse BOOK fact
            - definitive
        """
        # [Msg]: to get argument of Tokenized Fact as text
        title = fact.getArgumentAsText(isToUnquote=True)
        # [Msg]: to INITIALIZE Book
        self.book = Book(title)
        return self.book

    def parseAuthor(self, fact):
        """ to parse AUTHOR fact
        """
        # [Esc]: no book in context
        if not self.book:
            raise Error('AUTHOR fact outside BOOK context')
        # [Msg]: to get argument of Tokenized Fact as text
        self.book.author = fact.getArgumentAsText(isToUnquote=True)
        """ to parse VERSION fact
        """
        # [Esc]: no book in context
        if not self.book:
            raise Error('VERSION fact outside BOOK context')
        # [Msg]: to get argument of Tokenized Fact as text
        self.book.version = fact.getArgumentAsText(isToUnquote=True)
        return None

    def parseDate(self, fact):
        """ to parse DATE fact
        """
        # [Esc]: no book in context
        if not self.book:
            raise Error('DATE fact outside BOOK context')
        # [Msg]: to get argument of Tokenized Fact as text
        self.book.date = fact.getArgumentAsText(isToUnquote=True)
        return None

    def parseLogo(self, fact):
        """ to parse LOGO fact
        """
        # [Esc]: no book in context
        if not self.book:
            raise Error('LOGO fact outside BOOK context')
        # [Msg]: to get argument of Tokenized Fact as text
        self.book.logo = fact.getArgumentAsText(isToUnquote=True)
        return None

    def parseChapter(self, fact) -> Chapter:
        """ to parse CHAPTER fact
        """
        # [Esc]: no book in context
        if not self.book:
            raise Error('CHAPTER fact outside BOOK context')
        # [Msg]: to get argument of Tokenized Fact as text
        title = fact.getArgumentAsText(isToUnquote=True)
        # [Msg]: to INITIALIZE Chapter
        chapter = Chapter(title)
        # [Msg]: to add Chapter to Book
        self.book.addChapter(chapter)
        self._currentChapter = chapter
        self._currentSection = None
        self._currentPage = None
        self._currentContinuation = None
        return chapter

    def parseDescriptor(self, fact):
        """ to parse DESCRIPTOR fact
        """
        # [Msg]: to get argument of Tokenized Fact as text
        desc = fact.getArgumentAsText(isToUnquote=True)
        # [Alt]: apply to current section
        if self._currentSection:
            self._currentSection.descriptor = desc
        # [Alt]: apply to current chapter
        elif self._currentChapter:
            self._currentChapter.descriptor = desc
        return None

    def parsePrefix(self, fact):
        """ to parse PREFIX fact
        """
        # [Msg]: to get argument of Tokenized Fact as text
        prefix = fact.getArgumentAsText(isToUnquote=True)
        # [Alt]: apply to current page
        if self._currentPage:
            self._currentPage.prefix = prefix
        # [Alt]: apply to current section
        elif self._currentSection:
            self._currentSection.prefix = prefix
        # [Alt]: apply to current chapter
        elif self._currentChapter:
            self._currentChapter.prefix = prefix
        return None

    def parseSection(self, fact) -> Section:
        """ to parse SECTION fact
        """
        # [Esc]: no chapter in context
        if not self._currentChapter:
            raise Error('SECTION fact outside CHAPTER context')
        # [Msg]: to get argument of Tokenized Fact as text
        title = fact.getArgumentAsText(isToUnquote=True)
        # [Msg]: to INITIALIZE Section
        section = Section(title)
        # [Msg]: to add Section to Chapter
        self._currentChapter.addSection(section)
        self._currentSection = section
        self._currentPage = None
        self._currentContinuation = None
        return section

    def parseCrossReference(self, fact):
        """ to parse CROSS REFERENCE fact
        """
        # [Esc]: no section in context
        if not self._currentSection:
            raise Error('CROSS REFERENCE fact outside SECTION context')
        self._currentSection.isCrossReferenced = True
        return None

    def _addElement(self, fact, element: PageElement):
        """ to route a Page Element to its proper parent container
        """
        parentObj = fact.designPath[-1][1] if fact.designPath else None
        # [Alt]: apply to parent object
        if isinstance(parentObj, ElementContainer):
            parentObj.addElement(element)
        # [Alt]: apply to current continuation page
        elif self._currentContinuation:
            self._currentContinuation.addElement(element)
        # [Alt]: apply to current page
        elif self._currentPage:
            self._currentPage.addElement(element)

    def parsePage(self, fact) -> Page:
        """ to parse PAGE fact
        """
        # [Esc]: no section in context
        if not self._currentSection:
            raise Error('PAGE fact outside SECTION context')
        # [Msg]: to get argument of Tokenized Fact as text
        title = fact.getArgumentAsText(isToUnquote=True)
        # [Msg]: to INITIALIZE Foil Page
        page = Page(title)
        # [Msg]: to add Foil Page to Section
        self._currentSection.addPage(page)
        self._currentPage = page
        self._currentContinuation = None
        return page

    def parseCaption(self, fact):
        """ to parse CAPTION fact
        """
        # [Esc]: no page in context
        if not self._currentPage:
            raise Error('CAPTION fact outside PAGE context')
        # [Msg]: to get argument of Tokenized Fact as text
        self._currentPage.caption = fact.getArgumentAsText(isToUnquote=True)
        return None

    def parseHeader(self, fact):
        """ to parse HEADER fact
        """
        # [Msg]: to get argument of Tokenized Fact as text
        text = fact.getArgumentAsText(isToUnquote=True)
        # [Msg]: to INITIALIZE Header Page Element
        element = HeaderElement(text)
        self._addElement(fact, element)
        return element

    def parseText(self, fact):
        """ to parse TEXT fact
        """
        # [Msg]: to get argument of Tokenized Fact as text
        text = fact.getArgumentAsText(isToUnquote=True)
        # [Msg]: to INITIALIZE Text Page Element
        element = TextElement(text)
        self._addElement(fact, element)
        return element

    def parseEmphasized(self, fact):
        """ to parse EMPHASIZED fact
        """
        # [Msg]: to get argument of Tokenized Fact as text
        text = fact.getArgumentAsText(isToUnquote=True)
        # [Msg]: to INITIALIZE Emphasized Page Element
        element = EmphasizedElement(text)
        self._addElement(fact, element)
        return element

    def parseCode(self, fact):
        """ to parse CODE fact
        """
        # [Msg]: to get argument of Tokenized Fact as text
        text = fact.getArgumentAsText(isToUnquote=True)
        # [Msg]: to INITIALIZE Code Page Element
        element = CodeElement(text)
        self._addElement(fact, element)
        return element

    def parseCaptionLabel(self, fact):
        """ to parse CAPTION LABEL fact
        """
        # [Msg]: to get argument of Tokenized Fact as text
        text = fact.getArgumentAsText(isToUnquote=True)
        # [Msg]: to INITIALIZE Caption Label Page Element
        element = CaptionLabelElement(text)
        self._addElement(fact, element)
        return element

    def parseImage(self, fact):
        """ to parse IMAGE fact
        """
        # [Msg]: to get argument of Tokenized Fact as text
        fileName = fact.getArgumentAsText(isToUnquote=True)
        # [Msg]: to INITIALIZE Image Page Element
        element = ImageElement(fileName)
        self._addElement(fact, element)
        return element

    def parseAlt(self, fact):
        """ to parse ALT fact (image alt text)
        """
        # [Esc]: no page or continuation context
        target = self._currentContinuation or self._currentPage
        if not target or not target.elements:
            return None
        lastElement = target.elements[-1]
        if isinstance(lastElement, ImageElement):
            lastElement.altText = fact.getArgumentAsText(isToUnquote=True)
        return None

    def parseKeyword(self, fact):
        """ to parse KEYWORD fact
        """
        # [Esc]: no page in context
        if not self._currentPage:
            raise Error('KEYWORD fact outside PAGE context')
        # [Msg]: to get first label modifier of Tokenized Fact as text (ref type)
        refType = fact.getFirstLabelModifierAsText(isToUnquote=True) or 'Referenced'
        # [Msg]: to get argument of Tokenized Fact as text (keyword)
        keyword = fact.getArgumentAsText(isToUnquote=True)
        target = self._currentContinuation or self._currentPage
        target.keywords.append(KeywordRef(keyword, refType))
        return None

    def parseContinuation(self, fact) -> ContinuationPage:
        """ to parse CONTINUATION fact
        """
        # [Esc]: no page in context
        if not self._currentPage:
            raise Error('CONTINUATION fact outside PAGE context')
        # [Msg]: to add Continuation Page to Foil Page
        cont = self._currentPage.addContinuation()
        self._currentContinuation = cont
        return cont

    def parseRow(self, fact):
        """ to parse ROW fact
        """
        row = RowElement()
        self._addElement(fact, row)
        return row

    def parseCell(self, fact):
        """ to parse CELL fact
        """
        cell = CellElement()
        parentObj = fact.designPath[-1][1] if fact.designPath else None
        if hasattr(parentObj, 'addCell'):
            parentObj.addCell(cell)
        return cell

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(self, scriptPath: Path) -> Book:
        """ to parse educational site script from file
            - definitive [Part]
        """
        # [Msg]: to create Protonabu Snippet from file
        snippet = ProtonabuSnippetFromFile(scriptPath)
        # [Msg]: to compile Protonabu Fact source
        self.compile(snippet)
        # [Msg]: to parse tokenized Labeled Fact source
        self.parseLines(self._dispatcher)
        if not self.book:
            raise Error('No BOOK passfact found in educational site script', [('File', str(scriptPath))])
        return self.book

    def reverseEngineer(self, siteFolder: Path) -> Book:
        """ to reverse-engineer an existing educational site into the object model
        """
        # hook: walk the existing HTML site folder structure and reconstruct site model
        ...


def run(scriptPath: Path) -> Book:
    """ to parse educational site script
    """
    # [Msg]: to INITIALIZE Educational Site Parser
    parser = SiteParser()
    # [Msg]: to parse educational site script from file
    return parser.parse(scriptPath)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python -m nabu.protonabu.demoApp.siteParser <script.facts>')
        sys.exit(1)
    book = run(Path(sys.argv[1]))
    print(f'Parsed: {book.title} ({book.numChapters} chapters)')
