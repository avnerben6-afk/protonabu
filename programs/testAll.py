""" Module: Protonabu Comprehensive Unit-test
    - Author: Avner Ben
        - Created: 29-Aug-2026
            - Separated from Nabu
"""

import sys
from pathlib import Path

# Add src and tests root to sys.path
root_path = Path(__file__).resolve().parent.parent
src_path = root_path / 'src'
tests_path = root_path / 'tests'
for p in (src_path, tests_path):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from protonabu.testing import getTestModules, runTestModules

# Protonabu test suites
import testRawFact
import testProtonabuParser
import testLoops
import testStringUtil
import testSnippetAdapters
import testSiteGenerator


if __name__ == '__main__':
    modules, isRefresh = getTestModules(globals())
    runTestModules(modules, isRefresh)
