""" Module: Educational Site HTML Builder
    - Purpose: to render HTML page structure for the educational site generator
    - Author: Avner Ben
        - Created: 14-Apr-2026
            - Adapted from legacy educational site generator
    - Generator: Antigravity (Gemini 3.5 Flash)
       - Revised: 14-Apr-2026
"""

import html
import os
from typing import Optional, TextIO

# [Additional]
from .siteModel import (
    Book,
    Chapter,
    Section,
    Page,
    ContinuationPage
)


# CSS path placeholder — to be computed per page depth by SiteGenerator
CSS_PLACEHOLDER = '__CSS_PATH__'


class LeftColumn:
    """ Left Column
        - Intent: to render the Logo and Caption pane
    """
    def __init__(self, 
        book: Book, 
        chapter: Optional[Chapter] = None, 
        section: Optional[Section] = None, 
        page: Optional[Page] = None, 
        contLetter: str = '', 
        siteRoot: str = ''
    ):
        """ to INITIALIZE Left Column
            - Input: book
            - Input [Opt]: chapter
            - Input [Opt]: section
            - Input [Opt]: page
            - Input [Opt]: continuation letter
            - Input [Opt]: site root
        """
        # Contains [1:1 By Reference]: book
        self._book = book
        # Contains [1:1 By Reference]: chapter
        self._chapter = chapter
        # Contains [1:1 By Reference]: section
        self._section = section
        # Contains [1:1 By Reference]: Foil Page
        self._page = page
        self._contLetter = contLetter
        self._siteRoot = siteRoot

    def render(self) -> str:
        """ to render Left Column to HTML
        """
        imgSrc = ''
        # [Opt]: to Compute logo source
        if self._book.logo:
            logoName = os.path.basename(self._book.logo)
            imgSrc = f'{self._siteRoot}{logoName}'
        captionId = ''
        captionName = self._book.title
        # [Opt]: to compute caption identifier and name from page
        if self._page:
            captionId = f'{self._chapter.num}.{self._section.num}.{self._page.num}{self._contLetter}'
            captionName = self._page.caption or self._page.title
        # [Opt]: to compute caption identifier and name from section
        elif self._section:
            captionId = f'{self._chapter.num}.{self._section.num}'
            captionName = self._section.descriptor or self._section.title
        # [Opt]: to compute caption identifier and name from chapter
        elif self._chapter:
            captionId = str(self._chapter.num)
            captionName = self._chapter.descriptor or self._chapter.title
        logoHtml = ''
        # [Opt]: to build logo HTML with logo image
        if imgSrc:
            logoHtml = f'<img src="{imgSrc}" alt="{html.escape(self._book.title)} Logo" class="site-logo">\n'
        # [Opt]: to build logo HTML without logo image
        else:
            logoHtml = f'<div class="site-logo" style="text-align:center; padding: 2rem; color: #888;">[No Logo]</div>\n'
        return (
            '<div class="site-left">\n'
            f'  {logoHtml}'
            '  <div class="site-caption">\n'
            f'    <span class="site-caption-id">{captionId}</span>\n'
            f'    {html.escape(captionName)}\n'
            '  </div>\n'
            '</div>\n'
        )


class HtmlPage:
    """ HTML Page
        - Intent: to encapsulate the opening and closing skeleton of an HTML page
    """
    def __init__(
        self,
        outp: TextIO,
        title: str,
        cssPath: str,
        keywords: str = '',
        leftColumn: Optional[LeftColumn] = None
    ):
        """ to INITIALIZE HTML Page
            - Input: output stream
            - Input: page title
            - Input: CSS path
            - Input [Opt]: keywords
            - Input [Opt]: left column
        """
        self._outp: TextIO = outp
        self._title: str = title
        self._cssPath: str = cssPath
        self._keywords: str = keywords
        # Contains [1:1 By Reference]: left column
        self._leftColumn: Optional[LeftColumn] = leftColumn

    def __enter__(self) -> 'HtmlPage':
        """ to open HTML Page
            - Output: self
        """
        # [Msg]: to write HTML page header
        self._writeHeader()
        # [Msg]: to write HTML page wrapper and grid
        self.write('<div class="site-wrapper">\n<div class="site-grid">\n')
        # [Optt]: to render Left Column to HTML
        if self._leftColumn:
            self.write(self._leftColumn.render())
        # [Msg]: to write right column
        self.write('<div class="site-right">\n')
        return self

    def __exit__(self, *_):
        """ to close HTML Page
        """
        # [Msg]: to close right column
        self.write('</div>\n')
        # [Msg]: to close grid
        self.write('</div>\n')
        # [Msg]: to close wrapper
        self.write('</div>\n')
        # [Msg]: to write HTML page footer
        self._writeFooter()

    def write(self, s: str):
        """ to write HTML content to HTML Page
            - Input: HTML content
        """
        self._outp.write(s)

    def _writeHeader(self):
        """ to write HTML page header
        """
        kw = f'\n  <meta name="keywords" content="{html.escape(self._keywords)}">' if self._keywords else ''
        self._outp.write(
            f'<!DOCTYPE html>\n'
            f'<html lang="en">\n'
            f'<head>\n'
            f'  <meta charset="UTF-8">\n'
            f'  <meta name="viewport" content="width=device-width, initial-scale=1.0">{kw}\n'
            f'  <title>{html.escape(self._title)}</title>\n'
            f'  <link rel="stylesheet" href="{self._cssPath}">\n'
            f'</head>\n'
            f'<body>\n'
        )

    def _writeFooter(self):
        """ to write HTML page footer
        """
        self._outp.write('</body>\n</html>\n')


class NavPanel:
    """ Navigation Panel
        - Intent: to render the navigation header
        - Description: Navigation star + 4-row hierarchy
    """
    def __init__(
        self,
        book: Book,
        chapter: Optional[Chapter] = None,
        section: Optional[Section] = None,
        page: Optional[Page] = None,
        contLetter: str = '',
        siteRoot: str = '',
    ):
        """ to INITIALIZE Navigation Panel
            - Input: book
            - Input [Opt]: chapter
            - Input [Opt]: section
            - Input [Opt]: page
            - Input [Opt]: continuation letter
            - Input [Opt]: site root
        """
        # Contains [1:1 By Reference]: book
        self._book = book
        # Contains [1:1 By Reference]: chapter
        self._chapter = chapter
        # Contains [1:1 By Reference]: section
        self._section = section
        # Contains [1:1 By Reference]: Foil Page
        self._page = page
        self._contLetter = contLetter
        self._siteRoot = siteRoot

    def _navStar(self) -> str:
        """ to build Navigation Star (Up, Left, In, Right, Down)
        """
        # To reset navigation star elements
        up, left, inHref, right, down = '', '', '', '', ''
        # [Opt]: to compute In link for continuation
        if getattr(self._page, 'continuations', None) and not self._contLetter:
            inHref = f'{self._chapter.num}/{self._section.num}/{self._page.num}A.html'
        # [Opt]: to set page navigation star
        if self._page:
            ch, sec, pg = self._chapter.num, self._section.num, self._page.num
            # [Opt]: to set continuation page navigation star
            if self._contLetter:
                parentHref = f'{ch}/{sec}/{pg}.html'
                idx = next((i for i, c in enumerate(self._page.continuations) if c.letter == self._contLetter), -1)
                # [Opt]: to build parent anchor
                if idx != -1 and idx + 1 < len(self._page.continuations):
                    inHref = f'{ch}/{sec}/{pg}{self._page.continuations[idx+1].letter}.html'
                # [Opt]: to anchor to parent
                else:
                    inHref = parentHref
                up = left = right = down = ''
            # [Opt]: to set standard page navigation star
            else:
                up = f'{ch}/{sec}/0.html'
                if pg > 1: left = f'{ch}/{sec}/{pg-1}.html'
                # [Opt]: to set page right arrowhead
                if getattr(self._section, 'numPages', 0) and pg < self._section.numPages: 
                    right = f'{ch}/{sec}/{pg+1}.html'
        # [Opt]: to set section navigation star
        elif self._section:
            ch, sec = self._chapter.num, self._section.num
            up = f'{ch}/0.html'
            if sec > 1: left = f'{ch}/{sec-1}/0.html'
            # [Opt]: to set sectionright arrowhead
            if getattr(self._chapter, 'numSections', 0) and sec < self._chapter.numSections:
                right = f'{ch}/{sec+1}/0.html'
            # [Opt]: to set section down arrowhead
            if getattr(self._section, 'numPages', 0) > 0: 
                down = f'{ch}/{sec}/1.html'
        # [Opt]: to set chapter navigation star
        elif self._chapter:
            ch = self._chapter.num
            up = '0.html'
            # [Opt]: to set chapter left arrowhead
            if ch > 1: 
                left = f'{ch-1}/0.html'
            # [Opt]: to set chapter right arrowhead
            if ch < self._book.numChapters: 
                right = f'{ch+1}/0.html'
            # [Opt]: to set chapter down arrowhead
            if getattr(self._chapter, 'numSections', 0) > 0: 
                down = f'{ch}/1/0.html'
        # [Opt]: to set book navigation star
        elif getattr(self._book, 'numChapters', 0) > 0: 
            down = '1/0.html'

        def link(cls, pts, href, tooltip):
            color = '#0000cc' if href else '#999999'
            svg = f'<svg width="14" height="14" viewBox="0 0 14 14"><polygon points="{pts}" fill="{color}"/></svg>'
            # [Esc Done]: no href
            if not href: 
                return f'<span class="{cls} disabled" title="N/A">{svg}</span>'
            # o create link
            return f'<a href="{self._siteRoot}{href}" class="{cls}" title="{tooltip}">{svg}</a>'
        return (
            '<div class="nav-star">\n'
            f'  {link("nav-up", "7,1 1,13 13,13", up, "Up (Parent)")}\n'
            f'  {link("nav-left", "1,7 13,1 13,13", left, "Left (Previous peer)")}\n'
            f'  {link("nav-in", "4,4 10,4 10,10 4,10", inHref, "In (Continuations)")}\n'
            f'  {link("nav-right", "13,7 1,1 1,13", right, "Right (Next peer)")}\n'
            f'  {link("nav-down", "7,13 1,1 13,1", down, "Down (First child)")}\n'
            '</div>\n'
        )

    def _hierarchyHeader(self) -> str:
        """ to build 4-row hierarchical path
        """
        lines = ['<div class="nav-hierarchy">']

        def addRow(lvl, num, name, href):
            """ to add row to navigation hierarchy
                - Input: level
                - Input: number
                - Input: name
                - Input: href
            """
            h = f'{self._siteRoot}{href}' if href else ''
            linkHtml = f'<a href="{h}">{html.escape(name)}</a>' if href else html.escape(name)
            lines.append(
                f'  <div class="nav-hier-row nav-hier-{lvl}">'
                f'<div class="nav-hier-num">{num}</div>'
                f'<div class="nav-hier-name">{linkHtml}</div></div>'
            )

        # [Msg]: to add book row to navigation hierarchy
        addRow(1, '', self._book.title, '0.html')
        # [Msg; Opt]: to add chapter row to navigation hierarchy
        if self._chapter:
            addRow(2, str(self._chapter.num), self._chapter.title, f'{self._chapter.num}/0.html')
        # [Msg; Opt]: to add section row to navigation hierarchy
        if self._section:
            addRow(3, str(self._section.num), self._section.title, f'{self._chapter.num}/{self._section.num}/0.html')
        # [Msg; Opt]: to add page row to navigation hierarchy
        if self._page:
            addRow(4, str(self._page.num), self._page.title, '')
        lines.append('</div>\n')
        return '\n'.join(lines)

    def render(self) -> str:
        """ to render Navigation Panel to HTML
        """
        return (
            f'<nav class="site-nav">\n'
            f'  {self._navStar()}\n'
            f'  {self._hierarchyHeader()}\n'
            f'</nav>\n'
        )

class GlobalNav:
    """ Global Navigation
        - Intent: to render the global DFS "Next >" button in the footer
    """
    def __init__(self, nextHref: str, nextTitle: str, siteRoot: str = ''):
        """ to create Global Navigation
            - Input: nextHref - href of next page
            - Input: nextTitle - title of next page
            - Input: siteRoot - root of site
        """
        self._nextHref = nextHref
        self._nextTitle = nextTitle
        self._siteRoot = siteRoot

    def render(self) -> str:
        """ to render Global Navigation to HTML
        """
        # [Esc Done]: "no next href"
        if not self._nextHref:
            # to disable Global Navigation button
            return (
                f'<footer class="site-footer">\n'
                f'  <span class="global-next disabled" title="End of sequence" style="opacity: 0.5; cursor: not-allowed;">Next &rsaquo;</span>\n'
                f'</footer>\n'
            )
        return (
            f'<footer class="site-footer">\n'
            f'  <a href="{self._siteRoot}{self._nextHref}" class="global-next" title="Next in sequence">Next &rsaquo;</a>\n'
            f'</footer>\n'
        )


class TocTable:
    """ TOC Table
        - Intent: to render a table-of-contents listing (for section, chapter, or book index pages)
    """

    def __init__(self, levelName: str = 'Page'):
        """ to INITIALIZE TOC Table
        """
        self._levelName = levelName
        self._rows: list[tuple] = []

    def addRow(self, num: str, title: str, href: str, description: str = '', history: str = '', contSuffix: str = ''):
        """ to add TOC row to TOC Table
        """
        self._rows.append((num, title, href, description, history, contSuffix))

    def render(self) -> str:
        """ to render TOC Table to HTML
            - definitive [Part]
        """
        lines = [
            '<table class="toc-table">\n',
            '  <thead>\n',
            '    <tr>\n',
            f'      <th>#</th><th>{html.escape(self._levelName)} title</th>',
            '<th>Description</th><th>History</th>\n',
            '    </tr>\n',
            '  </thead>\n',
            '  <tbody>\n',
        ]
        # [Msg; scan "rows"]: to add TOC row to TOC Table
        for num, title, href, desc, hist, contSuffix in self._rows:
            lines.append('    <tr>\n')
            lines.append(f'      <td>{html.escape(str(num))}</td>\n')
            lines.append(f'      <td><a href="{href}">{html.escape(title)}</a></td>\n')
            descHtml = html.escape(desc)
            # [Opt contiuation]: to add continuation suffix to TOC line
            if contSuffix:
                descHtml += f'<i>{html.escape(contSuffix)}</i>'
            lines.append(f'      <td>{descHtml}</td>\n')
            lines.append(f'      <td class="toc-history">{html.escape(hist)}</td>\n')
            lines.append('    </tr>\n')
        lines.append('  </tbody>\n</table>\n')
        return ''.join(lines)


class CrossRefTable:
    """ Cross-Reference Table
        - Intent: to render the keyword cross-reference index for a section
    """

    REF_TYPES = ['Defined', 'Syntax', 'Explained', 'Referenced']

    def __init__(self):
        """ to INITIALIZE Cross-Reference Table
        """
        pass

    def render(self, keywordIndex: dict[str, dict[str, list]]) -> str:
        """ to render Cross-Reference Table to HTML
            - Input: keyword index
            - Output: HTML table
            - definitive [Part]
        """
        lines = [
            '<table class="xref-table">\n',
            '  <thead>\n',
            '    <tr>\n',
            '      <th>&nbsp;</th><th>Term / <code>KEYWORD</code></th>\n',
        ]
        # [Msg; Scan]: to add reference type column headers
        for rt in self.REF_TYPES:
            lines.append(f'      <th>{html.escape(rt)}</th>\n')
        lines.append('    </tr>\n  </thead>\n  <tbody>\n')
        prevLetter = ''
        # [Msg]: to add keyword row to Cross-Reference Table
        for kw in sorted(keywordIndex.keys(), key=lambda x: x.upper()):
            curLetter = kw[0].upper() if kw[0].isalpha() else '#'
            letterCell = curLetter if curLetter != prevLetter else '&nbsp;'
            prevLetter = curLetter
            fontTag = 'code' if kw == kw.upper() else 'span'
            lines.append('    <tr>\n')
            lines.append(f'      <td class="xref-letter">{letterCell}</td>\n')
            lines.append(f'      <td><{fontTag}>{html.escape(kw)}</{fontTag}></td>\n')
            # [Msg; Scan]: to add page number cells to keyword row
            for rt in self.REF_TYPES:
                pageNums = keywordIndex.get(kw, {}).get(rt, [])
                links = ', '.join(
                    f'<a href="{p}.html">{p}</a>' for p in pageNums
                )
                lines.append(f'      <td>{links}</td>\n')
            lines.append('    </tr>\n')
        lines.append('  </tbody>\n</table>\n')
        return ''.join(lines)


class PageContent:
    """ Page Content
        - Intent: to render the main content area of a foil page
    """

    def __init__(self, page: 'Page | ContinuationPage'):
        """ to INITIALIZE Page Content
        """
        # Contains [1:1 By Reference]: Foil Page
        self._page = page

    def render(self) -> str:
        """ to render Page Content to HTML
            - definitive [Part]
        """
        lines = ['<main class="foil-content">\n']
        # [Msg; Scan]: to render Page Element to HTML
        for element in self._page.elements:
            # [Msg]: to render <SUBSTITUTE> Page Element to HTML  (polymorphic dispatch)
            lines.append(element.renderHtml())
        lines.append('</main>\n')
        return ''.join(lines)

