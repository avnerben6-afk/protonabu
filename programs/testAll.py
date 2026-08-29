""" Module: Protonabu Comprehensive Unit-test
    - Author: Avner Ben
        - Created: 29-Aug-2026
            - Separated from Nabu
"""

import sys
from pathlib import Path

# Add src root to sys.path
root_path = Path(__file__).resolve().parent.parent
src_path = root_path / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from protonabu.testing import getTestModules, runTestModules

# Protonabu test suites residing with their respective products
from protonabu import testRawFact
from protonabu import testProtonabuParser
from protonabu import testLoops
from protonabu import testStringUtil
from protonabu.adapter import testSnippetAdapters
from protonabu.demoApp import testSiteGenerator


if __name__ == '__main__':
    modules, isRefresh = getTestModules(globals())
    runTestModules(modules, isRefresh)
