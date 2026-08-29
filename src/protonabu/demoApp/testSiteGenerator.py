""" Module: Educational Site Generator Test Module
    - Author: Avner Ben
        - Created: 24-Aug-2026
    - Generator: Antigravity (Gemini 3.7 Flash)
        - Generated: 24-Aug-2026
"""

import shutil
import unittest
from pathlib import Path

# [Additional]
from .siteModel import (
    Book, Chapter, Section, Page, TextElement, HeaderElement
)
# [Additional]
from .siteGenerator import SiteGenerator


class TwoPageSitePdfExportTestCase(unittest.TestCase):
    """ Two-Page Site PDF Export Test Case
    """

    def setUp(self):
        """ to set up test directory and site model
        """
        # to set up sandbox test directory under testArea
        self.testDir = Path(__file__).resolve().parents[3] / 'testArea' / 'test_site_pdf'
        # [Opt "directory exists"]: to remove previous test directory
        if self.testDir.exists():
            shutil.rmtree(self.testDir)
        self.testDir.mkdir(parents=True, exist_ok=True)

        # to construct two-page educational site model with mutual hyperlinks
        self.book = Book('Demo Hyperlinked Book', author='Avner Ben', version='v1')
        self.book.date = '24-Aug-2026'
        # [Msg]: to INITIALIZE chapter
        self.chapter = Chapter('Foundations', descriptor='Chapter 1 Descriptor')
        # [Msg]: to add Chapter to Book
        self.book.addChapter(self.chapter)
        # [Msg]: to INITIALIZE section
        self.section = Section('Basics', prefix='Intro')
        # [Msg]: to add Section to Chapter
        self.chapter.addSection(self.section)

        # Page 1 with explicit link pointing to Page 2
        # [Msg]: to INITIALIZE Foil Page
        self.page1 = Page('First Page', caption='First page caption')
        # [Msg]: to add Page Element to <Foil Page>
        self.page1.addElement(HeaderElement('Welcome to Page 1'))
        # [Msg]: to add Page Element to <Foil Page>
        self.page1.addElement(TextElement('This is the introductory page. See <a href="2.html">Second Page</a> for details.'))
        # [Msg]: to add Foil Page to Section
        self.section.addPage(self.page1)

        # Page 2 with explicit link pointing back to Page 1
        # [Msg]: to INITIALIZE Foil Page
        self.page2 = Page('Second Page', caption='Second page caption')
        # [Msg]: to add Page Element to <Foil Page>
        self.page2.addElement(HeaderElement('Welcome to Page 2'))
        # [Msg]: to add Page Element to <Foil Page>
        self.page2.addElement(TextElement('This is the detailed page. Return to <a href="1.html">First Page</a>.'))
        # [Msg]: to add Foil Page to Section
        self.section.addPage(self.page2)

    def tearDown(self):
        """ to tear down sandbox test directory
        """
        # [Opt "directory exists"]: to clean up test directory
        if self.testDir.exists():
            shutil.rmtree(self.testDir)

    def testGenerateAndExportPdf(self):
        """ to test site HTML generation and combined PDF export with internal hyperlinks
        """
        # [Msg]: to INITIALIZE Educational Site Generator
        generator = SiteGenerator(self.testDir)
        # [Msg]: to generate static HTML site from Book object model
        generator.generate(self.book)

        book_idx = self.testDir / '0.html'
        ch_idx = self.testDir / '1' / '0.html'
        sec_idx = self.testDir / '1' / '1' / '0.html'
        pg1 = self.testDir / '1' / '1' / '1.html'
        pg2 = self.testDir / '1' / '1' / '2.html'

        self.assertTrue(book_idx.exists(), 'Book index page 0.html must exist')
        self.assertTrue(ch_idx.exists(), 'Chapter index page 1/0.html must exist')
        self.assertTrue(sec_idx.exists(), 'Section index page 1/1/0.html must exist')
        self.assertTrue(pg1.exists(), 'Page 1 1/1/1.html must exist')
        self.assertTrue(pg2.exists(), 'Page 2 1/1/2.html must exist')

        pdf_path = self.testDir / 'two_page_site.pdf'
        # [Msg]: to export Educational Site to PDF
        exported_path = generator.exportToPdf(self.book, pdfPath=pdf_path)

        self.assertTrue(exported_path.exists(), 'Exported PDF file must exist')
        self.assertEqual(exported_path, pdf_path)
        file_size = exported_path.stat().st_size
        self.assertGreater(file_size, 1024, 'PDF file must not be empty')

        with open(exported_path, 'rb') as f:
            header = f.read(5)
            self.assertEqual(header, b'%PDF-', 'File header must match standard PDF signature')

        sec_pdf = self.testDir / 'section_1_1.pdf'
        # [Msg]: to export Educational Site to PDF
        exported_sec = generator.exportToPdf(self.section, pdfPath=sec_pdf)
        self.assertTrue(exported_sec.exists(), 'Exported Section PDF must exist')
        self.assertGreater(exported_sec.stat().st_size, 1024)


def suite() -> unittest.TestSuite:
    """ to build test suite
        - Output: test suite
    """
    return unittest.TestLoader().loadTestsFromTestCase(TwoPageSitePdfExportTestCase)


if __name__ == '__main__':
    unittest.main()
