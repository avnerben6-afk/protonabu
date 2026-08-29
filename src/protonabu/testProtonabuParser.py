""" Module: Protonabu Labeled-Fact Parser Test Module
    - Author: Avner Ben
        - Created: 17-Apr-2017
        - Improved: 24-Aug-2026
            - Prepared for release
    - Generator: Antigravity (Gemini 3.1 Pro)
        - Generated: 17-Apr-2017
        - Generator: Antigravity (Gemini 3.7 Flash)
            - Improved: 25-Aug-2026
"""

import io
import os
from pathlib import Path
import shutil
from typing import Optional, Iterator
import unittest

from .util.error import Error, InternalError, FactFileError
from .testing import test, TestBatch
# [Additional]
from . import tokenizedFact
# [Additional]
from . import factParser
from .rawFact import RawFact
from .tokenizedFact import TokenizedFact
from .factSnippet import (
    ProtonabuSnippet, 
    ProtonabuSnippetInMemory,
    ProtonabuMemorySource
)
# [Additional]
from .protonabuSchema import ProtonabuSchema
# [Additional]
from .protonabuParser import (
    SnippetParser,
    ProtonabuParser,
    ImportingProtonabuParser,
    ProtonabuParseDispatcher
)


class TestProtonabuParser(ImportingProtonabuParser):
    """ Test Protonabu Parser
        - Purpose: Trivial concrete class implementation to allow usage in test
    """

    def addImport(self, pathName: str, label: str, title: str): 
        """ to add import (test Protonabu Parser at 0036)
            - Input: path Name
            - Input: label
            - Input: title
        """
        pass # fake override


class ProtonabuSchemaTestCase(unittest.TestCase):
    """ Protonabu Schema Test Case
    """
    def __init__(self, methodName='runTest'):
        """ to INITIALIZE Protonabu Schema Test Case
            - Input [Opt "runTest"]: method Name
        """
        unittest.TestCase.__init__(self, methodName)
        # to set schema source (test Protonabu Parser at 0053)
        self.schemaSource = """
__SCHEMA_SECTION__: TOKENS
PRODUCT: quotedName
    USE CASE: quotedName
        TITLE: quotedName
        REQUIRES: quotedName
            REPEATED: quotedName
            OPTIONAL: quotedName?
            ALTERNATIVES: quotedName?
                REQUIRES: quotedName
                    __DITTO__: PRODUCT / USE CASE / REQUIRES
            OPTION: quotedName?
            USING: quotedName
            GIVING [quotedText?]: quotedName
            FROM: quotedName
            ESCAPE [quotedText?]: quotedText
                GIVING [quotedText?]: quotedName
            REQUIRES: quotedName
                __DITTO__: PRODUCT / USE CASE / REQUIRES
        """

    def setUp(self):
        """ to prepare to test Protonabu syntax Schema parsing
        """
        # [Guard]: to parse Test Protonabu schema
        try:
            # [Msg]: to parse Test Protonabu schema
            self.schema: ProtonabuSchema = self.initSchema()
        # [Esc Error]: "error"
        except FactFileError:
            raise

    def runTest(self):
        """ to test Protonabu syntax Schema parsing
        """
        outp = io.StringIO()
        # [Msg]: to dump Protonabu Schema for debug
        self.schema.dump(outp)
        # [Msg]: to compare dump with schema text
        actual = outp.getvalue().strip()
        outp.close()
        assert(actual == self.schemaSource.strip())

    def initSchema(self) -> ProtonabuSchema:
        """ to parse Test Protonabu schema
            - Output: result
        """
        # [Msg]: to INITIALIZE Protonabu Schema
        # - Using: to create Protonabu Snippet In Memory
        return ProtonabuSchema(
            ProtonabuSnippetInMemory(
                self.schemaSource.split('\n'),
                'Test Protonabu schema'
            )
        )


class ProtonabuTokenizeTestCase(ProtonabuSchemaTestCase):
    """ Protonabu Tokenize Test Case
    """
    DesignType = TestProtonabuParser
    homeFoler = None

    def __init__(self, methodName='runTest'):
        """ to INITIALIZE Protonabu Tokenize Test Case
            - Input [Opt "runTest"]: method Name
        """
        # [Msg]: to INITIALIZE Protonabu Schema Test Case
        ProtonabuSchemaTestCase.__init__(self, methodName)
        self.factSource = """
PRODUCT: A Product
    USE CASE: to parse nested bracketed expression
        REQUIRES: to set current sLabel and children
        REQUIRES: to evaluate current character
            REPEATED: "some text left"
            REQUIRES: to extract first character from line
                ESCAPE ["right bracket"]: DONE
                    GIVING: "to terminate parsing bracketed subexpression"
            ALTERNATIVES: unspecified
                REQUIRES: to parse nested bracketed expression
                    OPTION: "left bracket"
                    GIVING ["to append"]: "subtree"
                REQUIRES: to append to current sLabel
                    OPTION: "not a bracket"
                    GIVING ["to append"]: "current sLabel"
            """

    def setUp(self):
        """ to prepare to test Protonabu tokenizing
        """
        ProtonabuSchemaTestCase.setUp(self)
        # [msg]: to load test Protonabu Snippet
        self.inp: ProtonabuSnippet = self.initParse()
        # [Msg]: to INITIALIZE Protonabu Parser
        self.design = self.DesignType(self.schema, homeFolder=getattr(self, 'designPath', None))

    def runTest(self):
        """ to test Protonabu tokenizing
        """
        # [msg]: to compile Protonabu source
        self.design.compile(self.inp)
        outp = io.StringIO()
        # [Msg]: to dump tokenized Protonabu for debug
        self.design.dump(outp)
        actual = outp.getvalue().strip()
        assert(actual == self.factSource.strip())

    def initParse(self) -> ProtonabuSnippet:
        """ to load test Protonabu Snippet
            - Output: result
        """
        # [Msg]: to [Using; Using]: to protonabu snippet in memory
        inp = ProtonabuSnippetInMemory(
            self.factSource.split('\n'),
            'Protonabu File sanity test'
        )
        return inp


class SnippetParseTestCase(ProtonabuTokenizeTestCase):
    """ Base Snippet Parse Test Case
    """
    def __init__(self, methodName='runTest'):
        """ to INITIALIZE Base Snippet Parse Test Case
            - Input [Opt "runTest"]: method Name
        """
        # [Msg]: to INITIALIZE Protonabu Schema Test Case
        ProtonabuTokenizeTestCase.__init__(self, methodName)
        self.outp = None

    def setUp(self):
        """ to prepare to test Protonabu parsing
        """
        ProtonabuTokenizeTestCase.setUp(self)
        self.outp = io.StringIO()
        # [msg]: to load Protonabu line-parsing routines
        self.dispatcher: ProtonabuParseDispatcher = self.initDispatch()
        # [msg]: to compile Protonabu source
        self.design.compile(self.inp)

    def runTest(self):
        """ to test Protonabu parsing
        """
        if self.outp is None:
            self.outp = io.StringIO()
        # [msg]: to parse tokenized Protonabu source
        self.design.parseLines(self.dispatcher)
        actual = self.outp.getvalue().strip()
        assert(actual == self.factSource.strip())

    def initDispatch(self) -> ProtonabuParseDispatcher:
        """ to load Protonabu line-parsing routines
            - Output: result
        """
        self.design.immediateHandlers['IMPORTING'] = self.parseImporting
        # [Msg]: to INITIALIZE Protonabu Parse Dispatcher
        dispatcher = ProtonabuParseDispatcher()
        # [msg]: to find and register Protonabu line Parsers
        dispatcher.loadHandlers(self.schema.labels, self)
        return dispatcher

    def parseDummy(self, lineData: TokenizedFact, isQuoteArg: bool = False):
        """ to parse test any Protonabu Fact arguments
            - Input: line Data
            - Input [Opt "False"]: is Quote Arg
            - Output: result
        """
        offset = '    ' * len(lineData.designPath)
        line = f'{offset}{lineData.label}'
        # [Opt]: to set label modifier token itrs (test Protonabu Parser at 0200)
        if lineData.labelModifierTokenItrs:
            modifiers = '; '.join([f'"{tokenizedFact.parseQuotedName(x)}"' for x in lineData.labelModifierTokenItrs])
            line += f' [{modifiers}]'
        # [Opt]: to set argument token itr (test Protonabu Parser at 0203)
        if lineData.argumentTokenItr:
            arg = tokenizedFact.parseQuotedName(lineData.argumentTokenItr)
            # [Opt]: to set is quote arg (test Protonabu Parser at 0205)
            if arg and isQuoteArg:
                arg = f'"{arg}"'
            line += f': {arg}'
            # [Opt]: to set arg modifier token itrs (test Protonabu Parser at 0208)
            if lineData.argModifierTokenItrs:
                modifiers = '; '.join([f'"{tokenizedFact.parseQuotedName(x)}"' for x in lineData.argModifierTokenItrs])
                line += f' [{modifiers}]'
        if self.outp is not None:
            self.outp.write(line + '\n')
        return None

    def parseImporting(self,
        lineData: TokenizedFact,
        itr: Optional[Iterator[RawFact]]
    ):
        """ to parse dummy prerequisite design immediate directive
            - Input: line Data
            - Input: itr
        """
        # [Msg]: to parse import immediate directive
        self.design.parseImportingDirective(lineData, itr)

    def parseProduct(self, lineData: TokenizedFact):
        """ to parse dummy product design fact
            - Input: line Data
            - Output: result
        """
        # [Msg]: to parse test any Protonabu Fact arguments | USING=line Data
        return self.parseDummy(lineData)

    def parseUseCase(self, lineData: TokenizedFact):
        """ to parse dummy use case design fact
            - Input: line Data
            - Output: result
        """
        # [Msg]: to parse test any Protonabu Fact arguments | USING=line Data
        return self.parseDummy(lineData)

    def parseTitle(self, lineData: TokenizedFact):
        """ to parse dummy title design fact
            - Input: line Data
            - Output: result
        """
        # [Msg]: to parse test any Protonabu Fact arguments | USING=line Data
        return self.parseDummy(lineData)

    def parseRequires(self, lineData: TokenizedFact):
        """ to parse dummy requires design fact
            - Input: line Data
            - Output: result
        """
        # [Msg]: to parse test any Protonabu Fact arguments | USING=line Data
        return self.parseDummy(lineData)

    def parseConditions(self, lineData: TokenizedFact):
        """ to parse dummy conditions design fact
            - Input: line Data
            - Output: result
        """
        # [Msg]: to parse test any Protonabu Fact arguments | USING=line Data | USING=true
        return self.parseDummy(lineData, True)

    def parseRepeated(self, lineData: TokenizedFact):
        """ to parse dummy repeated design fact
            - Input: line Data
            - Output: result
        """
        # [Msg]: to parse test any Protonabu Fact arguments | USING=line Data | USING=true
        return self.parseDummy(lineData, True)

    def parseOptional(self, lineData: TokenizedFact):
        """ to parse dummy optional design fact
            - Input: line Data
            - Output: result
        """
        # [Msg]: to parse test any Protonabu Fact arguments | USING=line Data | USING=true
        return self.parseDummy(lineData, True)

    def parseOption(self, lineData: TokenizedFact):
        """ to parse dummy option design fact
            - Input: line Data
            - Output: result
        """
        # [Msg]: to parse test any Protonabu Fact arguments | USING=line Data | USING=true
        return self.parseDummy(lineData, True)

    def parseAlternatives(self, lineData: TokenizedFact):
        """ to parse dummy alternatives design fact
            - Input: line Data
            - Output: result
        """
        # [Msg]: to parse test any Protonabu Fact arguments | USING=line Data
        return self.parseDummy(lineData)

    def parseUsing(self, lineData: TokenizedFact):
        """ to parse dummy using design fact
            - Input: line Data
            - Output: result
        """
        # [Msg]: to parse test any Protonabu Fact arguments | USING=line Data | USING=true
        return self.parseDummy(lineData, True)

    def parseGiving(self, lineData: TokenizedFact):
        """ to parse dummy giving design fact
            - Input: line Data
            - Output: result
        """
        # [Msg]: to parse test any Protonabu Fact arguments | USING=line Data | USING=true
        return self.parseDummy(lineData, True)

    def parseFrom(self, lineData: TokenizedFact):
        """ to parse dummy from design fact
            - Input: line Data
            - Output: result
        """
        # [Msg]: to parse test any Protonabu Fact arguments | USING=line Data | USING=true
        return self.parseDummy(lineData, True)

    def parseEscape(self, lineData: TokenizedFact):
        """ to parse dummy escape design fact
            - Input: line Data
            - Output: result
        """
        # [Msg]: to parse test any Protonabu Fact arguments | USING=line Data
        return self.parseDummy(lineData)

class ProtonabuParseTestCase(SnippetParseTestCase):
    """ Protonabu Parse Test Case
    """
    DesignType = TestProtonabuParser

    def __init__(self, methodName='runTest'):
        """ to INITIALIZE Protonabu Parse Test Case
            - Input [Opt "runTest"]: method Name
        """
        # [Msg]: to INITIALIZE Base Protonabu Parse Test Case
        SnippetParseTestCase.__init__(self, methodName)
        self.importSource = """
PRODUCT: Another Product
    PART: Another Part
        CAPABILITY: to evaluate another character
"""

    def setUp(self):
        """ to prepare to test Protonabu parsing of imports
        """
        # to extend test-case schema syntax...
        schemaSource = self.schemaSource.split('\n')
        schemaSource.insert(3, '        CAPABILITY: quotedName')
        schemaSource.insert(3, '    PART: quotedName')
        schemaSource.insert(1, 'IMPORTING: quotedPathName')
        schemaSource.insert(1, '__SCHEMA_SECTION__: IMMEDIATE')
        self.schemaSource = '\n'.join(schemaSource)
        # ...to extend test-case schema syntax

        # to add import directive to test-case source...
        designSource = self.factSource.split('\n')
        designSource.insert(1, 'IMPORTING: "user/sampleInsert.facts"')
        designSource.append('        REQUIRES: to evaluate another character')
        self.factSource = '\n'.join(x for x in designSource if x.strip())
        # ...to add import directive to test-case source

        # to write test-case import library on the disk
        self.designPath = Path(__file__).resolve().parents[2] / 'testArea' / 'protonabu'
        path = self.designPath / 'user'
        path.mkdir(parents=True, exist_ok=True)
        with open(path / "sampleInsert.facts", 'w') as outp:
            outp.write(self.importSource)
        # [Msg]: to prepare to test Protonabu parsing
        SnippetParseTestCase.setUp(self)

    def tearDown(self):
        """ to remove test-case files
        """
        # [Opt]: to set exists (test Protonabu Parser at 0331)
        if hasattr(self, 'designPath') and self.designPath.exists():
            shutil.rmtree(self.designPath)


    def runTest(self):
        """ to test Protonabu parsing of imports
        """
        self.outp = io.StringIO()
        # [msg]: to parse tokenized Protonabu source
        self.design.parseLines(self.dispatcher)
        actual = self.outp.getvalue().strip()
        expected = self.factSource.strip().split('\n')
        expected[0:1] = self.importSource.strip().split('\n')
        expected = '\n'.join(expected)
        assert(actual == expected)

    def parseUsing(self, lineData: TokenizedFact):
        """ to parse dummy using design fact in import test
            - Input: line Data
            - Output: result
        """
        # [Msg]: to parse test any Protonabu Fact arguments | USING=line Data
        return self.parseDummy(lineData)

    def parsePart(self, lineData: TokenizedFact):
        """ to parse dummy part design fact in import test
            - Input: line Data
            - Output: result
        """
        # [Msg]: to parse test any Protonabu Fact arguments | USING=line Data
        return self.parseDummy(lineData)

    def parseCapability(self, lineData: TokenizedFact):
        """ to parse capability (test Protonabu Parser at 0357)
            - Input: line Data
            - Output: result
        """
        # [Msg]: to parse test any Protonabu Fact arguments | USING=line Data
        return self.parseDummy(lineData)


class MultipleModifierTestCase(ProtonabuParseTestCase):
    """ Multiple Modifier Test Case
        - Description: Tests that the parser correctly handles multiple modifiers on a fact.
        - Input: line Data
    """
    DesignType = TestProtonabuParser

    def setUp(self):
        """ to prepare to test multiple-modifier Fact parsing
        """
        self.schemaSource = self.schemaSource.replace('GIVING [quotedText?]', 'GIVING [fraction; quotedText?]')
        ProtonabuTokenizeTestCase.setUp(self)
        # [msg]: to load Protonabu line-parsing routines
        self.dispatcher: ProtonabuParseDispatcher = self.initDispatch()
        self.design.compile(self.inp)

    def runTest(self):
        """ to test bad multiple-modifier parsing
        """
        self.outp = io.StringIO()
        # [msg]: to compile Labeled Fact source
        self.assertRaises(
            Error,
            self.design.parseLines,
            self.dispatcher
        )


class ExitValidatorTestCase(unittest.TestCase):
    """ Exit Validator Test Case
    """
    def runTest(self):
        """ to test Exit Validators mechanism
        """
        # to initialize schema and parser
        schema_src = """
__SCHEMA_SECTION__: TOKENS
PRODUCT: quotedName
"""
        # [Msg]: to INITIALIZE Protonabu Schema
        # - Using: to create Protonabu Snippet In Memory
        schema = ProtonabuSchema(ProtonabuSnippetInMemory(schema_src.split('\n'), 'Test Schema'))
        class MyTestParser(TestProtonabuParser):
            """ My Test Parser
            """
            def parseProduct(self, lineData):
                """ to parse dummy Product fact in Exit Validator Test
                    - Input: lineData
                """
                pass
        # [Msg]: to INITIALIZE my test parser
        parser = MyTestParser(schema)
        snippet_src = """
PRODUCT: "Test Product"
"""
        # [Msg]: to create Protonabu Snippet In Memory
        snippet = ProtonabuSnippetInMemory(snippet_src.split('\n'), 'Test Snippet')
        # [Msg]: to compile Protonabu Fact source
        parser.compile(snippet)
        validated_objs = []
        def validator(obj):
            validated_objs.append(obj)
        dummy_obj_1 = "dummy1"
        dummy_obj_2 = "dummy2"
        # to defer parsed-object validation to fact-base completion
        # [Msg]: to register exit validator
        parser.registerExitValidator(dummy_obj_1, validator)
        # to defer parsed-object validation to fact-base completion
        # [Msg]: to register exit validator
        parser.registerExitValidator(dummy_obj_2, validator)
        # to forget parsed-object deferred validation
        # [Msg]: to unregister exit validator
        parser.unregisterExitValidator(dummy_obj_2)
        # [Msg]: to INITIALIZE Protonabu Parse Dispatcher
        dispatcher = ProtonabuParseDispatcher()
        # [Msg]: to load parser handlers from schema
        dispatcher.loadHandlers(schema.labels, parser)
        # [Msg]: to parse tokenized Protonabu Fact source
        parser.parseLines(dispatcher)
        # to verify that only dummy_obj_1 was validated 
        # [Msg]: to assert equal
        self.assertEqual(validated_objs, [dummy_obj_1])
        # [Msg]: to INITIALIZE Snippet Parser
        snippet_parser = SnippetParser(schema)
        # [Msg]: to compile Snippet Parser source
        snippet_parser.compile(snippet)
        snippet_validated = []
        # [Msg]: to register exit validator
        snippet_parser.registerExitValidator(dummy_obj_1, lambda obj: snippet_validated.append(obj))
        # [Msg]: to parse tokenized Labeled Fact source
        snippet_parser.parseLines(dispatcher)
        # [Msg]: to assert equal
        self.assertEqual(snippet_validated, [dummy_obj_1])


class ApostropheParsingTestCase(unittest.TestCase):
    """ Apostrophe Parsing Test Case
    """
    def runTest(self):
        """ to test unquoted Italian apostrophe parsing
        """
        schema_src = """
__SCHEMA_SECTION__: TOKENS
PRODUCT: unstructuredText
"""
        # [Msg]: to [Using]: to protonabu schema
        schema = ProtonabuSchema(ProtonabuSnippetInMemory(schema_src.split('\n'), 'Test Schema'))
        
        parsed_args = []
        class MyTestParser(TestProtonabuParser):
            """ My Test Parser
            """
            def parseProduct(self, lineData):
                """ to parse product (test Protonabu Parser at 0541)
                    - Input: line Data
                """
                parsed_args.append(tokenizedFact.parseUniqueEntityName(lineData.argumentTokenItr))
        
        # [Msg]: to INITIALIZE my test parser
        parser = MyTestParser(schema)
        snippet_src = """
PRODUCT: l'esempio dell'arte
"""
        # [Msg]: to [Using; Using]: to protonabu snippet in memory
        snippet = ProtonabuSnippetInMemory(snippet_src.split('\n'), 'Test Snippet')
        parser.compile(snippet)
        
        # [Msg]: to protonabu parse dispatcher
        dispatcher = ProtonabuParseDispatcher()
        dispatcher.loadHandlers(schema.labels, parser)
        parser.parseLines(dispatcher)
        
        # [Msg]: to [Using; Using]: to assert equal
        self.assertEqual(parsed_args, ["l'esempio dell'arte"])


class ErrorProtocolTestCase(unittest.TestCase):
    """ Error Protocol Preservation Test Case
    """
    def runTest(self):
        """ to test error fields and file attribute preservation
        """
        # Test Error field preservation when wrapping/re-raising
        # [Msg]: to [Using; Using]: to error
        err1 = Error('Invalid label in fact', [
            ('Label', 'TRAVERSAL'),
            ('File', '/path/to/project.nabu:811')
        ])
        err1.set('Path', 'PRODUCT / PART / CONTAINS')
        
        # Test re-raising Error(err1)
        # [Msg]: to [Using]: to error
        err2 = Error(err1)
        # [Msg]: to [Using; Using]: to assert equal
        self.assertEqual(err2.origMessage, 'Invalid label in fact!')
        # [Msg]: to [Using; Using]: to assert equal
        self.assertEqual(err2.get('File'), '/path/to/project.nabu:811')
        # [Msg]: to [Using; Using]: to assert equal
        self.assertEqual(err2.get('Path'), 'PRODUCT / PART / CONTAINS')
        
        # to test FactFileError with object and fields
        class MockFact:
            """ Mock Fact
            """
            fileName = '/path/to/mock.nabu'
            lineNumber = 42
        
        # [Msg]: to [Using; Using; Using]: to fact file error
        ffe = FactFileError(MockFact(), 'Syntax error', fields=err1.fields)
        # [Msg]: to [Using; Using]: to assert equal
        self.assertEqual(ffe.get('file'), '/path/to/mock.nabu:42')
        # [Msg]: to [Using; Using]: to assert equal
        self.assertEqual(ffe.get('Label'), 'TRAVERSAL')


class CompileFromSourceTestCase(unittest.TestCase):
    """ Compile From Source Test Case
    """
    def runTest(self):
        """ to test compiling directly from an ISource
        """
        schema_src = """
__SCHEMA_SECTION__: TOKENS
PRODUCT: quotedName
"""
        schema = ProtonabuSchema(
            ProtonabuSnippetInMemory(schema_src.strip().split('\n'), 'Test Schema')
        )
        parser = ProtonabuParser(schema)
        source = ProtonabuMemorySource(['PRODUCT: "MyProduct"'])
        # [Msg]: to compile Protonabu Parser source from ISource directly
        parser.compile(source)
        self.assertEqual(parser.numFrames, 1)


class MissingSchemaLabelIntegrityTestCase(unittest.TestCase):
    """ Missing Schema Label Integrity Test Case
    """
    def runTest(self):
        """ to test fail-fast InternalError when AST TokenList has missing schema Label
        """
        schema_src = """
__SCHEMA_SECTION__: TOKENS
PRODUCT: quotedName
"""
        schema = ProtonabuSchema(
            ProtonabuSnippetInMemory(schema_src.strip().split('\n'), 'Test Schema')
        )
        parser = SnippetParser(schema)
        # Synthetic AST node with label=None
        corrupted_frame = parser.TokenList(None, None)
        parser.frames.children.append(corrupted_frame)
        dispatcher = ProtonabuParseDispatcher()
        with self.assertRaises(InternalError) as ctx:
            parser.parseLines(dispatcher)
        self.assertIn('Corrupted AST node: missing schema Label', str(ctx.exception))


class MissingLineIntegrityTestCase(unittest.TestCase):
    """ Missing Line Integrity Test Case
    """
    def runTest(self):
        """ to test that AST TokenList missing line data raises InternalError
        """
        schema_src = """
__SCHEMA_SECTION__: TOKENS
PRODUCT: quotedName
"""
        schema = ProtonabuSchema(
            ProtonabuSnippetInMemory(schema_src.strip().split('\n'), 'Test Schema')
        )
        parser = SnippetParser(schema)
        prod_label = schema.index['PRODUCT']
        # Synthetic AST node with valid label but line=None
        corrupted_frame = parser.TokenList(None, prod_label)
        parser.frames.children.append(corrupted_frame)
        dispatcher = ProtonabuParseDispatcher()
        with self.assertRaises(InternalError) as ctx:
            parser.parseLines(dispatcher)
        self.assertIn('Corrupted AST node: missing line data', str(ctx.exception))


class FrameLineIntegrityTestCase(unittest.TestCase):
    """ Frame Line Integrity Test Case
    """
    def runTest(self):
        """ to test that AST TokenList with TokenizedFact parses and sets isFirst correctly
        """
        schema_src = """
__SCHEMA_SECTION__: TOKENS
PRODUCT: quotedName
"""
        schema = ProtonabuSchema(
            ProtonabuSnippetInMemory(schema_src.strip().split('\n'), 'Test Schema')
        )
        parser = SnippetParser(schema)
        prod_label = schema.index['PRODUCT']
        raw = RawFact(label='PRODUCT', arg='"MyProduct"')
        tok = TokenizedFact(raw, ['PRODUCT'], 1, 'test.nabu', 1)
        tok.label = 'PRODUCT'
        frame = parser.TokenList(tok, prod_label)
        parser.frames.children.append(frame)

        called = []
        class TestDispatcher(ProtonabuParseDispatcher):
            def __init__(self):
                super().__init__()
                self.handlers['PRODUCT'] = (self.beginProduct, None)
            def beginProduct(self, factParser):
                called.append(factParser.isFirst)

        dispatcher = TestDispatcher()
        parser.parseLines(dispatcher)
        self.assertEqual(called, [True])


class InvalidRankParentGuardTestCase(unittest.TestCase):
    """ Invalid Rank Parent Guard Test Case
    """
    def runTest(self):
        """ to test that fact with invalid rank or missing parent raises Error
        """
        schema_src = """
__SCHEMA_SECTION__: TOKENS
PRODUCT: quotedName
"""
        schema = ProtonabuSchema(
            ProtonabuSnippetInMemory(schema_src.strip().split('\n'), 'Test Schema')
        )
        parser = SnippetParser(schema)
        raw = RawFact(label='PRODUCT', arg='"MyProduct"')
        raw.rank = 0
        raw.lineNumber = 1
        raw.fileName = 'test.nabu'

        class MockSnippet(ProtonabuSnippet):
            def __init__(self):
                self.parsingStack = None
            def __iter__(self):
                yield raw

        with self.assertRaises(Error) as ctx:
            parser.compile(MockSnippet())
        self.assertIn('missing parent container', str(ctx.exception))


class UncompiledImportDirectiveTestCase(unittest.TestCase):
    """ Uncompiled Import Directive Test Case
    """
    def runTest(self):
        """ to test that uncompiled import directive raises InternalError
        """
        schema_src = """
__SCHEMA_SECTION__: TOKENS
PRODUCT: quotedName
"""
        schema = ProtonabuSchema(
            ProtonabuSnippetInMemory(schema_src.strip().split('\n'), 'Test Schema')
        )
        parser = TestProtonabuParser(schema)
        demo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'demoApp', 'example', 'demo_site.facts'))
        raw = RawFact(label='IMPORTING', arg=f'"{demo_path}"')
        raw.rank = 1
        raw.lineNumber = 1
        raw.fileName = 'test.nabu'
        tok = TokenizedFact(raw, ['IMPORTING'], 1, 'test.nabu', 1)

        with self.assertRaises(InternalError) as ctx:
            parser.parseImportingDirective(tok, None)
        self.assertIn('Parser has no active input snippet for importing', str(ctx.exception))


def main(isRefreshExpectedTestData: bool = False)-> tuple[bool, int]:
    """ to perform Protonabu Parser Test Cases
        - Input: refresh expected test-data flag
        - Output: "Result state"
        - Contains: Success indicator
        - Contains: number of test cases
    """
    # [Msg]: to perform Unit Test
    return test(
        TestBatch(
            (ProtonabuSchemaTestCase, ['runTest'], isRefreshExpectedTestData),
            (ProtonabuTokenizeTestCase, ['runTest'], isRefreshExpectedTestData),
            (ProtonabuParseTestCase, ['runTest'], isRefreshExpectedTestData),
            (MultipleModifierTestCase, ['runTest'], isRefreshExpectedTestData),
            (ExitValidatorTestCase, ['runTest'], isRefreshExpectedTestData),
            (ApostropheParsingTestCase, ['runTest'], isRefreshExpectedTestData),
            (ErrorProtocolTestCase, ['runTest'], isRefreshExpectedTestData),
            (CompileFromSourceTestCase, ['runTest'], isRefreshExpectedTestData),
            (MissingSchemaLabelIntegrityTestCase, ['runTest'], isRefreshExpectedTestData),
            (MissingLineIntegrityTestCase, ['runTest'], isRefreshExpectedTestData),
            (FrameLineIntegrityTestCase, ['runTest'], isRefreshExpectedTestData),
            (InvalidRankParentGuardTestCase, ['runTest'], isRefreshExpectedTestData),
            (UncompiledImportDirectiveTestCase, ['runTest'], isRefreshExpectedTestData)
        )
    )

# [Opt]: to perform Protonabu Parser Test Cases
if __name__ == '__main__':
    main()