""" Module: Educational Site Generator Main
    - Purpose: to provide CLI access to the Educational Site Generator
    - Usage: python -m nabu.protonabu.demoApp <script.facts> <output_folder>
    - Author: Avner Ben
        - Created: 14-Apr-2026
        - Improved: 24-Aug-2026
            - Prepared for release
    - Generator: Antigravity (Gemini 3.5 Flash)
        - Generated: 14-Apr-2026
"""

import sys
from pathlib import Path

from ..util.error import Error
# [Additional]
from .siteGenerator import generate


class EducationalSiteGeneratorCLI:
    """ Educational Site Generator CLI
    """

    @staticmethod
    def main():
        """ to run Educational Site Generator from command line
        """
        # [Esc Done]: Help
        if len(sys.argv) < 3:
            print('Usage: python -m nabu.protonabu.demoApp <script.facts> <output_folder>')
            print()
            print('  <script.facts>   Protonabu educational site script file')
            print('  <output_folder>  Destination folder for generated HTML site')
            sys.exit(1)
        scriptPath = Path(sys.argv[1])
        outputRoot = Path(sys.argv[2])
        # [Esc Error]: script file not found
        if not scriptPath.exists():
            print(f'Error: Script file not found: {scriptPath}')
            sys.exit(1)
        try:
            # [Msg]: to generate educational site from script file
            book = generate(scriptPath, outputRoot)
            print(f'Site generated: {book.title}')
            print(f'  Chapters: {book.numChapters}')
            print(f'  Output:   {outputRoot}')
            print(f'  Open:     {outputRoot / "0.html"}')
        # [Esc Error]: unsuccessful
        except Error as err:
            print(f'Error: {err}')
            sys.exit(1)


def main():
    """ to run Educational Site Generator CLI
    """
    # [Msg]: to run Educational Site Generator from command line
    EducationalSiteGeneratorCLI.main()


if __name__ == '__main__':
    main()
