""" Module: Educational Site Generator
    - Purpose: to generate a static HTML educational site from a Book object model
    - Author: Avner Ben
        - Created: 14-Apr-2026
    - Generator: Antigravity (Gemini 3.5 Flash)
        - Generated: 14-Apr-2026
"""

import html
import shutil
from pathlib import Path
from typing import Optional

# [Additional]
from .siteModel import Book, Chapter, Section, Page, ContinuationPage, ImageElement
# [Additional]
from .htmlBuilder import (
    HtmlPage, NavPanel, TocTable, CrossRefTable, PageContent,
    LeftColumn, GlobalNav
)
# [Additional]
from .pdfExporter import PdfExporter
# [Additional]
from .siteParser import SiteParser

_CSS_FILE = 'styles.css'
_CSS_SOURCE = Path(__file__).parent / _CSS_FILE


class SiteGenerator:
    """ Educational Site Generator
        - Intent: to walk the Book object model and emit a self-contained static HTML site
        - Stereotype: Composite
    """

    def __init__(self, outputRoot: Path, scriptRoot: Optional[Path] = None):
        """ to INITIALIZE Educational Site Generator
            - Input: output Root
            - Input [Opt "None"]: script Root
        """
        self.outputRoot: Path = outputRoot
        self.scriptRoot: Optional[Path] = scriptRoot
        # [Msg]: to INITIALIZE Educational Site PDF Exporter
        self.pdfExporter: PdfExporter = PdfExporter(outputRoot)
        outputRoot.mkdir(parents=True, exist_ok=True)

    def generate(self, book: Book):
        """ to generate static HTML site from Book object model
            - Input: Book
            - Output [State]: static HTML site
            - definitive [Product]
        """
        # [Msg "copy CSS to site root"]: to handle copy CSS to site root
        self._copyCss()
        # [Msg "build flat DFS node list rest"]: to handle build flat DFS node list for Global Next
        self._buildDfs(book)
        # [Msg]: to copy logo from snippet path to site root
        self._copyLogo(book)
        # [Msg]: to generate Book index page
        self._generateBookIndex(book)
        # [Scan]: to generate Chapter pages
        for chapter in book.chapters:
            # [Msg]: to generate Chapter index page
            self._generateChapterIndex(book, chapter)
            # [Scan]: to generate Section pages
            for section in chapter.sections:
                # [Msg]: to generate Section index page
                self._generateSectionIndex(book, chapter, section)
                # [Scan]: to generate Foil pages
                for page in section.pages:
                    # [Msg]: to generate Foil page
                    self._generateFoilPage(book, chapter, section, page)
                    # [Scan]: to generate Continuation pages
                    for cont in page.continuations:
                        # [Msg]: to generate Continuation page
                        self._generateContinuationPage(book, chapter, section, page, cont)
                # [Opt]: to generate Cross-Reference page
                if section.isCrossReferenced:
                    # [Msg]: to generate Cross-Reference page
                    self.generateCrossReference(book, chapter, section)

    def _copyCss(self):
        """ to copy CSS file to site root
        """
        destCss = self.outputRoot / _CSS_FILE
        shutil.copy2(_CSS_SOURCE, destCss)

    def _copyLogo(self, book: Book):
        """ to copy logo from snippet path to site root
            - Input: book
        """
        # [Esc Done]: no logo
        if not book.logo: return
        src = Path(book.logo)
        # [Opt "relative paths"]: to base logo path
        if not src.is_absolute():
            # to base logo path to the facts script directory
            base = self.scriptRoot if self.scriptRoot else Path.cwd()
            src = base / src
        # [Opt "logo exists"]: to copy logo to site root
        if src.exists():
            dest = self.outputRoot / src.name
            # [Opt]: to do copy logo to site root
            if not dest.exists():
                shutil.copy2(src, dest)

    def _buildDfs(self, book: Book):
        """ to build flat DFS node list for Global Next
            - Input: book
        """
        self._dfsList = []
        self._dfsList.append(('0.html', book.title))
        # [Scan]: to build DFS list for chapter
        for ch in book.chapters:
            self._dfsList.append((f'{ch.num}/0.html', ch.title))
            # [Scan]: to build DFS list for section
            for sec in ch.sections:
                self._dfsList.append((f'{ch.num}/{sec.num}/0.html', sec.title))
                # [Scan]: to build DFS list for page
                for pg in sec.pages:
                    self._dfsList.append((f'{ch.num}/{sec.num}/{pg.num}.html', pg.title))

    def _getNextDfs(self, currentHref: str) -> tuple[str, str]:
        """ to retrieve next node from DFS list
            - Input: current href
            - Output: next node
        """
        # [Scan]: to find current node in DFS list
        for i, (href, title) in enumerate(self._dfsList):
            # [Esc Done]: "beyond end" 
            if href == currentHref:
                # [Esc Done]: "no next node"
                if i + 1 < len(self._dfsList):
                    return self._dfsList[i+1]
                break
        # [Msg]: to get next dfs (site Generator at 0134)
        return ('', '')

    def _generateBookIndex(self, book: Book):
        """ to generate Book index page
            - Output [state]: Book index page
            - Input: book
            - definitive [Part]
        """
        path = self.outputRoot / '0.html'
        cssPath = _CSS_FILE
        title = book.title
        with open(path, 'w', encoding='utf-8') as f:
            # [Msg]: to INITIALIZE Left Column
            leftCol = LeftColumn(book, siteRoot='')
            # [Ctxt HTML Page]: to generate Book index page
            with HtmlPage(f, title, cssPath, leftColumn=leftCol) as pg:
                # [Msg]: to render Navigation Panel
                pg.write(NavPanel(book, siteRoot='').render())
                # [Msg]: to write Book title
                pg.write(f'<h1 class="foil-title">{html.escape(title)}</h1>\n')
                # [Opt]: to write author
                if book.author:
                    pg.write(f'<p class="foil-caption-label"><i>Author: {html.escape(book.author)}</i></p>\n')
                # [Opt]: to write version
                if book.version:
                    pg.write(f'<p class="foil-caption-label"><i>Version: {html.escape(book.version)}</i></p>\n')
                # [Opt]: to write date
                if getattr(book, 'date', ''):
                    pg.write(f'<p class="foil-caption-label"><i>Date: {html.escape(book.date)}</i></p>\n')
                pg.write('<hr class="page-rule">\n')
                # [Msg]: to initialize TOC table
                toc = TocTable('Chapter')
                # [Scan]: to format and add row to TOC table
                for chapter in book.chapters:
                    href = f'{chapter.num}/0.html'
                    desc = chapter.descriptor
                    # [Msg]: to add row to TOC table
                    toc.addRow(chapter.num, chapter.title, href, desc)
                pg.write(toc.render())
                pg.write('<hr class="page-rule">\n')
                pg.write(GlobalNav(*self._getNextDfs('0.html'), siteRoot='').render())

    def _generateChapterIndex(self, book: Book, chapter: Chapter):
        """ to generate Chapter index page
            - Input: Book
            - Input: Chapter
            - Output [state]: Chapter index page
        """
        # [Msg]: to create chapter directory
        chDir = self.outputRoot / str(chapter.num)
        chDir.mkdir(parents=True, exist_ok=True)
        # [Msg]: to open chapter index page for writing
        path = chDir / '0.html'
        cssPath = '../' + _CSS_FILE
        siteRoot = '../'
        title = f'{book.title} / {chapter.title}'
        with open(path, 'w', encoding='utf-8') as f:
            # [Msg]: to initialize left column
            leftCol = LeftColumn(book, chapter, siteRoot=siteRoot)
            # [Ctxt HTML Page]: to generate Chapter index page
            with HtmlPage(f, title, cssPath, leftColumn=leftCol) as pg:
                # [Msg]: to render navigation panel
                pg.write(NavPanel(book, chapter, siteRoot=siteRoot).render())
                # [Msg]: to write chapter title
                pg.write(f'<h1 class="foil-title">{html.escape(chapter.title)}</h1>\n')
                pg.write('<hr class="page-rule">\n')
                # [Msg]: to initialize TOC table
                toc = TocTable('Section')
                # [Scan]: to format and add row to TOC table
                for section in chapter.sections:
                    href = f'{section.num}/0.html'
                    desc = section.descriptor
                    # [Msg]: to add row to TOC table
                    toc.addRow(section.num, section.title, href, desc)
                pg.write(toc.render())
                pg.write('<hr class="page-rule">\n')
                # [Msg]: to render global navigation
                pg.write(GlobalNav(*self._getNextDfs(f'{chapter.num}/0.html'), siteRoot=siteRoot).render())

    def _generateSectionIndex(self, book: Book, chapter: Chapter, section: Section):
        """ to generate Section index page
            - Input: Book
            - Input: Chapter
            - Input: Section
            - Output [state]: Section index page
        """
        # [Msg]: to create section directory
        secDir = self.outputRoot / str(chapter.num) / str(section.num)
        secDir.mkdir(parents=True, exist_ok=True)
        path = secDir / '0.html'
        cssPath = '../../' + _CSS_FILE
        siteRoot = '../../'
        title = f'{book.title} / {chapter.title} / {section.title}'
        with open(path, 'w', encoding='utf-8') as f:
            # [Msg]: to initialize left column
            leftCol = LeftColumn(book, chapter, section, siteRoot=siteRoot)
            # [Ctxt HTML Page]: to generate Section index page
            with HtmlPage(f, title, cssPath, leftColumn=leftCol) as pg:
                # [Msg]: to render navigation panel
                pg.write(NavPanel(book, chapter, section, siteRoot=siteRoot).render())
                # [Msg]: to write section title
                pg.write(f'<h1 class="foil-title">{html.escape(section.title)}</h1>\n')
                pg.write('<hr class="page-rule">\n')
                # [Msg]: to initialize TOC table
                toc = TocTable('Page')
                # [Scan]: to format and add row to TOC table
                for page in section.pages:
                    href = f'{page.num}.html'
                    desc = page.caption
                    contSuffix = ''
                    # [Opt]: to add continuation suffix
                    if page.hasContinuation:
                        contSuffix = f' (+{page.numContinuations} continuation{"s" if page.numContinuations > 1 else ""} page)'
                    # [Msg]: to add row to TOC table
                    toc.addRow(page.num, page.title, href, desc, contSuffix=contSuffix)
                # [Opt]: to add cross-reference row
                if section.isCrossReferenced:
                    # [Msg]: to add cross-reference row
                    toc.addRow('', 'Cross-reference index', 'xref.html', 'Keyword index for this section')
                pg.write(toc.render())
                pg.write('<hr class="page-rule">\n')
                pg.write(GlobalNav(*self._getNextDfs(f'{chapter.num}/{section.num}/0.html'), siteRoot=siteRoot).render())

    def _generateFoilPage(self, book: Book, chapter: Chapter, section: Section, page: Page):
        """ to generate Foil page
            - Input: Book
            - Input: Chapter
            - Input: Section
            - Input: Page
            - Output [state]: Foil page
            - definitive
        """
        # [Msg]: to create section directory
        secDir = self.outputRoot / str(chapter.num) / str(section.num)
        # [Msg]: to copy image files to section directory
        self._copyImages(page, secDir)
        path = secDir / f'{page.num}.html'
        cssPath = '../../' + _CSS_FILE
        siteRoot = '../../'
        title = f'{book.title} / {chapter.title} / {section.title} / {page.title}'
        kwStr = ', '.join(k.keyword for k in page.keywords) if page.keywords else ''
        with open(path, 'w', encoding='utf-8') as f:
            leftCol = LeftColumn(book, chapter, section, page, siteRoot=siteRoot)
            # [Ctxt HTML Page]: to generate Foil page
            with HtmlPage(f, title, cssPath, keywords=kwStr, leftColumn=leftCol) as pg:
                pg.write(NavPanel(book, chapter, section, page, siteRoot=siteRoot).render())
                pg.write('  <div class="foil-title-block">\n')
                pg.write(f'    <h2 class="foil-title">{html.escape(page.title)}</h2>\n')
                pg.write('    <hr class="foil-divider">\n')
                pg.write('  </div>\n')
                pg.write('<div class="foil-content">\n')
                pg.write('  <div class="foil-content-body">\n')
                # [Msg]: to INITIALIZE Page Content
                pg.write(PageContent(page).render())
                pg.write('  </div>\n</div>\n')
                pg.write('<hr class="page-rule">\n')
                # [Msg]: to create Global Navigation
                pg.write(GlobalNav(*self._getNextDfs(f'{chapter.num}/{section.num}/{page.num}.html'), siteRoot=siteRoot).render())

    def _generateContinuationPage(
        self,
        book: Book,
        chapter: Chapter,
        section: Section,
        page: Page,
        cont: ContinuationPage
    ):
        """ to generate Continuation page
            - Input: Book
            - Input: Chapter
            - Input: Section
            - Input: Page
            - Input: Continuation Page
            - Output [state]: Continuation page
        """
        # [Msg]: to create section directory
        secDir = self.outputRoot / str(chapter.num) / str(section.num)
        # [Msg]: to copy images
        self._copyImages(cont, secDir)
        path = secDir / f'{page.num}{cont.letter}.html'
        cssPath = '../../' + _CSS_FILE
        siteRoot = '../../'
        title = f'{book.title} / {chapter.title} / {section.title} / {page.title} (cont.)'
        idx = page.continuations.index(cont)
        with open(path, 'w', encoding='utf-8') as f:
            # [Msg]: to initialize left column
            leftCol = LeftColumn(book, chapter, section, page, contLetter=cont.letter, siteRoot=siteRoot)
            # [Ctxt HTML Page]: to generate Continuation page
            with HtmlPage(f, title, cssPath, leftColumn=leftCol) as pg:
                # [Msg]: to INITIALIZE navigation panel
                pg.write(NavPanel(book, chapter, section, page, contLetter=cont.letter, siteRoot=siteRoot).render())
                pg.write('  <div class="foil-title-block">\n')
                pg.write(
                    f'    <h2 class="foil-title">{html.escape(page.title)} '
                    f'<small>(cont. {cont.letter})</small></h2>\n'
                )
                pg.write('    <hr class="foil-divider">\n')
                pg.write('  </div>\n')
                pg.write('<div class="foil-content">\n')
                pg.write('  <div class="foil-content-body">\n')
                # [Msg]: to initialize Page Content
                pg.write(PageContent(cont).render())
                pg.write('  </div>\n</div>\n')
                pg.write('<hr class="page-rule">\n')

    def generateCrossReference(self, book: Book, chapter: Chapter, section: Section):
        """ to generate Cross-Reference keyword index page for a Section
            - Input: Book
            - Input: Chapter
            - Input: Section
            - Output [state]: Cross-Reference page
        """
        # [Msg]: to create section directory
        secDir = self.outputRoot / str(chapter.num) / str(section.num)
        path = secDir / 'xref.html'
        cssPath = '../../' + _CSS_FILE
        siteRoot = '../../'
        title = f'{book.title} / {chapter.title} / {section.title} / Cross-Reference'
        # [Msg]: to collect all keyword references across all pages and continuations in Section
        keywordIndex = section.collectKeywords()
        with open(path, 'w', encoding='utf-8') as f:
            # [Msg]: to initialize left column
            leftCol = LeftColumn(book, chapter, section, siteRoot=siteRoot)
            # [Ctxt HTML Page]: to generate Cross-Reference keyword index page for a Section
            with HtmlPage(f, title, cssPath, leftColumn=leftCol) as pg:
                # [Msg]: to INITIALIZE navigation panel
                pg.write(NavPanel(book, chapter, section, siteRoot=siteRoot).render())
                pg.write(f'<h1 class="foil-title">Cross-Reference: {html.escape(section.title)}</h1>\n')
                pg.write('<hr class="page-rule">\n')
                # [Msg]: to initialize Cross Reference Table
                pg.write(CrossRefTable().render(keywordIndex))
                pg.write('<hr class="page-rule">\n')

    def exportToPdf(self,
        unit: Optional[Book | Chapter | Section | Page] = None,
        pdfPath: Optional[Path] = None
    ) -> Path:
        """ to export Educational Site to PDF
            - Input [Opt]: site unit (defaults to full Book)
            - Input [Opt]: target output PDF path
            - Output: Path to generated PDF file
        """
        # [Msg]: to export site unit to PDF
        return self.pdfExporter.exportToPdf(unit=unit, pdfPath=pdfPath)

    def embedVisual(self, page: Page, visualName: str):
        """ to embed a third-party API-generated visual into a Foil Page
            - Input: page
            - Input: visual Name
        """
        # to embed visual (site Generator at 0655)
        pass

    def _copyImages(self, pageOrCont, secDir: Path):
        """ to copy image files referenced in page to section output directory
            - Input: page or continuation page
            - Input: section output directory
            - Output [state]: image files copied
        """
        # [Scan]: to do copy page image files
        for element in getattr(pageOrCont, 'elements', []):
            # [Esc Once]: "not image"
            if not isinstance(element, ImageElement): continue
            srcFile = Path(element.fileName)
            # [Opt "absolute path and exists"]: to copy image file
            if srcFile.is_absolute() and srcFile.exists():
                destFile = secDir / srcFile.name
                # [Opt "not exists"]: to do copy image file physically
                if not destFile.exists():
                    shutil.copy2(srcFile, destFile)
                element.fileName = srcFile.name  # make relative to section


def generate(scriptPath: Path, outputRoot: Path) -> Book:
    """ to generate educational site from script file
        - Input: script path
        - Input: output root
        - Output: Book
    """
    # [Msg]: to INITIALIZE Educational Site Parser
    parser = SiteParser()
    # [Msg]: to parse educational site script from file
    book = parser.parse(scriptPath)
    # [Msg]: to INITIALIZE Educational Site Generator
    generator = SiteGenerator(outputRoot, scriptRoot=scriptPath.parent)
    # [Msg]: to generate static HTML site from Book object model
    generator.generate(book)
    return book
