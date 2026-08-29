""" Module: Educational Site PDF Exporter
    - Purpose: to export educational site pages to a single combined PDF document with internal hyperlinks
    - Author: Avner Ben
        - Created: 24-Aug-2026
    - Generator: Antigravity (Gemini 3.7 Flash)
        - Generated: 24-Aug-2026
"""

import html
import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from ..config import config
# [Additional]
from .siteModel import Book, Chapter, Section, Page

_CSS_FILE = 'styles.css'


class PdfExporter:
    """ Educational Site PDF Exporter
        - Intent: to compile generated static HTML pages in DFS order into a single PDF document
    """

    def __init__(self, outputRoot: Path):
        """ to INITIALIZE Educational Site PDF Exporter
            - Input: output Root
        """
        self.outputRoot: Path = outputRoot

    def exportToPdf(self,
        unit: Optional[Book | Chapter | Section | Page] = None,
        pdfPath: Optional[Path] = None
    ) -> Path:
        """ to export site unit to PDF
            - Input [Opt]: site unit (defaults to full Book)
            - Input [Opt]: target output PDF path
            - Output: Path to generated PDF file
            - definitive [Part]
        """
        # [Msg]: to collect HTML files in DFS order for the given unit
        html_files = self._collectUnitHtmlFiles(unit)
        # [Esc Error]: no HTML files found
        if not html_files:
            raise FileNotFoundError('No generated HTML files found to export to PDF')

        # to assign internal anchor IDs for each HTML file
        path_to_anchor: dict[str, str] = {}
        # [Scan]: to map relative HTML file paths to internal anchor identifiers
        for p in html_files:
            try:
                rel = p.relative_to(self.outputRoot)
            except ValueError:
                rel = Path(p.name)
            anchor_id = 'page_' + re.sub(r'[^a-zA-Z0-9_-]', '_', str(rel))
            path_to_anchor[str(rel)] = anchor_id

        combined_bodies: list[str] = []
        # [Scan]: to extract and link body content from each HTML page
        for p in html_files:
            try:
                rel = p.relative_to(self.outputRoot)
            except ValueError:
                rel = Path(p.name)
            anchor_id = path_to_anchor[str(rel)]
            content = p.read_text(encoding='utf-8', errors='ignore')

            body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
            body_content = body_match.group(1) if body_match else content

            # to rewrite relative hrefs to internal anchors
            def replace_href(m):
                href = m.group(1)
                # [Esc]: external link or in-page anchor
                if href.startswith(('#', 'http://', 'https://', 'mailto:', 'javascript:')):
                    return f'href="{href}"'
                target_path = (p.parent / href).resolve()
                try:
                    target_rel = str(target_path.relative_to(self.outputRoot))
                    # [Opt "target in anchor map"]: to rewrite relative link to internal anchor
                    if target_rel in path_to_anchor:
                        return f'href="#{path_to_anchor[target_rel]}"'
                except Exception:
                    pass
                return f'href="{href}"'

            # to rewrite relative image and media src to root-relative paths
            def replace_src(m):
                src = m.group(1)
                # [Esc]: absolute or remote src
                if src.startswith(('http://', 'https://', 'data:', '/')):
                    return f'src="{src}"'
                target_path = (p.parent / src).resolve()
                try:
                    target_rel = str(target_path.relative_to(self.outputRoot))
                    return f'src="{target_rel}"'
                except Exception:
                    return f'src="{src}"'

            body_content = re.sub(r'href=[\"\']([^\"\']+)[\"\']', replace_href, body_content)
            body_content = re.sub(r'src=[\"\']([^\"\']+)[\"\']', replace_src, body_content)

            combined_bodies.append(
                f'<div class="pdf-page-container" id="{anchor_id}" style="page-break-after: always; break-after: page;">\n{body_content}\n</div>'
            )

        title = getattr(unit, 'title', 'Document') if unit else 'Document'
        full_html_content = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{_CSS_FILE}">
<style>
@page {{
    size: A4 landscape;
    margin: 10mm;
}}
@media print {{
    .pdf-page-container {{ page-break-after: always; break-after: page; }}
    table {{ page-break-inside: auto; break-inside: auto; }}
    thead {{ display: table-header-group !important; }}
    tbody {{ display: table-row-group !important; }}
    tr {{ page-break-inside: avoid; break-inside: avoid; }}
}}
body {{
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
}}
</style>
</head>
<body>
{''.join(combined_bodies)}
</body>
</html>'''

        temp_html_path = self.outputRoot / '_pdf_combined.html'
        out_pdf = pdfPath if pdfPath else self.outputRoot / f'{re.sub(r"[^a-zA-Z0-9_-]", "_", title)}.pdf'
        temp_pdf_path = out_pdf.with_suffix('.tmp.pdf')

        # [Guard]: to run headless Chrome PDF conversion
        try:
            # [Msg]: to get Chrome or Chromium executable path
            chrome_bin = config.getChromiumPath()
            # [Esc Error]: Chrome executable not found
            if not chrome_bin:
                raise FileNotFoundError('Chrome or Chromium executable not found for PDF export')

            cmd = [
                str(chrome_bin),
                '--headless',
                '--no-sandbox',
                '--disable-gpu',
                '--print-to-pdf-no-header',
                f'--print-to-pdf={temp_pdf_path.resolve()}',
                f'file://{temp_html_path.resolve()}'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            # [Esc Error]: Chrome execution failed
            if result.returncode != 0:
                raise RuntimeError(f'Chrome PDF export failed with code {result.returncode}: {result.stderr}')

            # [Opt "atomic rename"]: to move temporary PDF to destination
            if temp_pdf_path.exists():
                if out_pdf.exists():
                    out_pdf.unlink()
                shutil.move(str(temp_pdf_path), str(out_pdf))
            return out_pdf
        finally:
            # [Scan]: to clean temporary PDF export artifacts
            for tf in [temp_html_path, temp_pdf_path]:
                if tf.exists():
                    try:
                        tf.unlink()
                    except Exception:
                        pass

    def _collectUnitHtmlFiles(self,
        unit: Optional[Book | Chapter | Section | Page] = None
    ) -> list[Path]:
        """ to collect HTML files in DFS order for the given unit
            - Input [Opt]: unit
            - Output: list of HTML file paths
        """
        files: list[Path] = []
        # [Opt "Book or None"]: to collect Book HTML files
        if unit is None or isinstance(unit, Book):
            book_idx = self.outputRoot / '0.html'
            if book_idx.exists():
                files.append(book_idx)
            chapters = unit.chapters if isinstance(unit, Book) else []
            # [Scan]: to collect each Chapter in Book
            for ch in chapters:
                files.extend(self._collectUnitHtmlFiles(ch))
            # [Opt "fallback"]: to scan output root for HTML files
            if not files:
                for p in sorted(self.outputRoot.rglob('*.html')):
                    if not p.name.startswith('_'):
                        files.append(p)
        # [Opt "Chapter"]: to collect Chapter HTML files
        elif isinstance(unit, Chapter):
            ch_idx = self.outputRoot / f'{unit.num}/0.html'
            if ch_idx.exists():
                files.append(ch_idx)
            # [Scan]: to collect each Section in Chapter
            for sec in unit.sections:
                files.extend(self._collectUnitHtmlFiles(sec))
        # [Opt "Section"]: to collect Section HTML files
        elif isinstance(unit, Section):
            ch_num = unit.chapter.num if hasattr(unit, 'chapter') and unit.chapter else 1
            sec_idx = self.outputRoot / f'{ch_num}/{unit.num}/0.html'
            if sec_idx.exists():
                files.append(sec_idx)
            # [Scan]: to collect each Page in Section
            for pg in unit.pages:
                files.extend(self._collectUnitHtmlFiles(pg))
            # [Opt "cross referenced"]: to collect Section Cross-Reference page
            if getattr(unit, 'isCrossReferenced', False):
                xref = self.outputRoot / f'{ch_num}/{unit.num}/xref.html'
                if xref.exists():
                    files.append(xref)
        # [Opt "Page"]: to collect Page HTML files
        elif isinstance(unit, Page):
            ch_num = unit.chapter.num if hasattr(unit, 'chapter') and unit.chapter else 1
            sec_num = unit.section.num if hasattr(unit, 'section') and unit.section else 1
            pg_path = self.outputRoot / f'{ch_num}/{sec_num}/{unit.num}.html'
            if pg_path.exists():
                files.append(pg_path)
            # [Scan]: to collect continuation pages
            for cont in getattr(unit, 'continuations', []):
                cont_path = self.outputRoot / f'{ch_num}/{sec_num}/{unit.num}{cont.letter}.html'
                if cont_path.exists():
                    files.append(cont_path)
        return files
