""" Module: Protonabu Schema Report Module
    - Purpose: To report Protonabu-schema annotated parse-tree EBNF to markdown.
    - Author: Avner Ben
        - Created: 28-Apr-2026
            - Separated from fact Snippet Parser
        - Revised: 28-Apr-2026
        - Improved: 24-Aug-2026
            - Prepared for release
    - Generator: Antigravity (Gemini 3.7 Flash)
        - Improved: 28-Aug-2026
            - Decoupled from Nabu DOM configuration
"""


import os
import re
import subprocess
import sys
from typing import Any, Optional

from .config import config
from .util.stringUtil import nameMaker
# [Additional]
from .primitiveTokens import basicTypeNames, tokenLegend
# [Additional]
from .protonabuSchema import ProtonabuSchema, Label, DittoLabel


_visitedTokenizers: Optional[set[str]] = None

def reportSchema(schema: ProtonabuSchema, outp=None):
    """ to report parse tree
        - Input: schema
        - Input [Opt]: output stream
    """
    global _visitedTokenizers

    # [Opt]: to restore literate name from programmatic name
    if _visitedTokenizers is None:
        _visitedTokenizers = {
            nameMaker.unMakeProgrammaticName(x, upper=True) 
                for x in basicTypeNames
        }
    # [Scan]: to reset visited Tokenizer
    definedTokenizers: dict[str, str] = {
        x: '' for x in _visitedTokenizers
    }

    # [Scan]: to invert visited tokenizer key and value
    invertedIndex: dict[Label, str] = {
        v: k for (k, v) in schema.index.items()
    }

    def reportNode(
        node: Label,
        visited: list[Label],
        index: dict[Label, str],
        ranks: list[int]
    ):
        """ to report Protonabu schema under Label
            - Input: node
            - Input: visited
            - Input: index
            - Input: ranks
        """
        def processTokenizerName(s: str) -> tuple[str, str]:
            """ to prepare tokenizer name for printout
                - Input: tokenizer name
                - Output: tokenizer and parent name
                - Contains: tokenizer name
                - Contains: parent name
            """
            # [Esc Done]: empty tokenizer name
            if not s: return s, ''
            # [Alt]: to format optional tokenizer postfix
            if s.endswith('?'):
                s = s[:-1]
                postfix = ' *(optional)*'
            # [Alt]: to format empty tokenizer postfix
            else:
                postfix = ''
            # [Msg]: to restore literate name from programmatic names
            s = nameMaker.unMakeProgrammaticName(s, upper=True)
            # [Guard]: to retrieve parent tokenizer name from defined tokenizers
            try:
                parentName = definedTokenizers[s]
            # [Esc Ignored]: to update defined tokenizers
            except KeyError:
                parentName = ''
                definedTokenizers[s] = invertedIndex[node]
            return s + postfix, parentName

        def printTokenizer(
            title: str,
            tokenizer: tuple[str, str],
            func: Any,
            leadIn: str = ''
        ):
            """ to print Protonabu schema Label tokenizer list
                - Input: title
                - Input: tokenizer
                - Input: func
                - Input: lead-in
            """
            # [Msg]: to start doc tokenizer line
            outp.write(f'{leadIn}- *{title}:*')
            tokenizerName, parentName = tokenizer
            # [Msg]: to write doc tokenizer name
            outp.write(f' {tokenizerName}')
            descriptor = tokenLegend.get(func, '').strip()
            if descriptor:
                # [Alt]: to format tokenizer descriptor inner bullet
                if descriptor.startswith('- '):
                    outp.write(':\n    ')
                    descriptor = descriptor.replace('\n-', '\n    -')
                # [Alt]: to format tokenizer main descriptor bullet
                else:
                    outp.write(' - ')
                # [Msg]: to write doc tokenizer descriptor
                outp.write(descriptor)
            outp.write('\n')
            # [Opt]: to write doc parent tokenizer name
            if parentName:
                outp.write(f'{leadIn}    - (defined in {parentName})\n')

        def sanitize(name: str) -> str:
            """ to sanitize EBNF node name
                - Input: name
                - Output: sanitized name
            """
            return re.sub(r'[^a-zA-Z0-9]', '_', name)

        def printGraphicEbnf():
            """ to print graphic EBNF diagram
            """
            # [Esc Done]: unnamed node or stdout stream
            if not node.name or not hasattr(outp, 'name') or outp.name == '<stdout>':
                return
            # [Msg]: to sanitize EBNF node name
            # - Using: file prefix
            filePrefix = sanitize("_".join(v.name for v in visited) + "_" + node.name) if visited else sanitize(node.name)
            # [Msg]: to sanitize EBNF node name
            # - Using: rule name
            ruleName = sanitize(node.name)
            # to get the output directory
            out_dir = os.path.dirname(outp.name)
            # [Opt]: to set schema-doc output directory to current directory
            if not out_dir: 
                out_dir = '.'
            # to create path to the PlantUML EBNF diagram
            puml_path = os.path.join(out_dir, f'{filePrefix}_schema.puml')
            # to get path to the PlantUML jar
            jar_path = config.get('thirdparty', 'plantuml')
            # [Esc Done]: PlantUML jar not configured or not found
            if not jar_path or not os.path.exists(jar_path):
                return
            # [Guard]: to generate doc EBNF diagram
            try:
                with open(puml_path, 'w', encoding='utf-8') as pf:
                    # to write EBNF start
                    pf.write('@startebnf\n')
                    rhs = []
                    # [Opt]: to add label modifier 
                    if getattr(node, 'labelModifierTokenizer', None):
                        mname = str(node.labelModifierTokenizer)
                        rhs.append(f'"{mname}"' if not mname.endswith('?') else f'["{mname[:-1]}"]')
                    # [Opt]: to add argument
                    if getattr(node, 'argumentTokenizer', None):
                        aname = str(node.argumentTokenizer)
                        rhs.append(f'"{aname}"' if not aname.endswith('?') else f'["{aname[:-1]}"]')
                    # [Opt]: to add argument modifier to doc EBNF
                    if getattr(node, 'argModifierTokenizer', None):
                        mname = str(node.argModifierTokenizer)
                        rhs.append(f'"{mname}"' if not mname.endswith('?') else f'["{mname[:-1]}"]')
                    childrenStr = []
                    # [Scan]: to prepare children for doc EBNF
                    for child in node:
                        # [Alt]: to set schema path
                        if child.tokenList and isinstance(child.tokenList[0], DittoLabel):
                            # [Scan "index"; Opt "child match"]: to pick path element
                            path = [x[0] for x in index.items() if x[1] == child.tokenList[0].tokenList[0]]
                            # [Opt]: to set report Schema path 
                            if path: childrenStr.append(path[0])
                        # [Alt]: to prepare child token for doc EBNF
                        else:
                            childrenStr.append(child.name)
                    # [Opt]: to join children for doc EBNF
                    if childrenStr:
                        joined = " | ".join([sanitize(c) for c in childrenStr])
                        rhs.append(f"{{ {joined} }}")
                    # [Opt]: to prepare empty child token for doc EBNF
                    if not rhs:
                        rhs.append("''")
                    # to write child EBNF
                    pf.write(f'{ruleName} = ' + " , ".join(rhs) + " ;\n")
                    # to write EBNF end
                    pf.write('@endebnf\n')
                # to run the PlantUML jar
                subprocess.run(['java', '-jar', jar_path, '-tsvg', puml_path], check=False, close_fds=False)
                outp.write(f'![{node.name}]({filePrefix}_schema.svg)\n\n')
            # [Esc Warning]: to handle exception
            except Exception as e:
                print(f'PlantUML generation failed for {filePrefix}: {e}')

        # [Esc]: ditto node
        if node.tokenList and isinstance(node.tokenList[0], DittoLabel): return
        # [Opt]: to start writing doc node
        if node.name:
            # to format doc node path
            path = '.'.join([str(x) for x in ranks])
            # to format doc node title
            title = invertedIndex[node].split(' / ')
            title[-1] = f'<u>{title[-1]}</u>'
            title = ' / '.join(title)
            # [Msg]: to write doc node header
            outp.write(f'### {path}. {title}\n')
            # [Opt]: to write doc node function
            if node.function:
                outp.write(f'- *Function:* {node.function}\n')
            # [Opt]: to print Protonabu schema Label tokenizer list
            if node.labelModifierTokenizer:
                printTokenizer(
                    'Label modifier',
                    processTokenizerName(str(node.labelModifierTokenizer)),
                    node.labelModifierTokenizer.func
                )
            # [Opt]: to write doc node argument tokenizer
            if node.argumentTokenizer:
                # [Msg]: to print Protonabu schema Label tokenizer list
                printTokenizer(
                    'Argument',
                    processTokenizerName(str(node.argumentTokenizer)),
                    node.argumentTokenizer.func
                )
                # [Msg; Opt]: to write doc node argument modifier tokenizer
                if node.argModifierTokenizer:
                    printTokenizer(
                        'Argument modifier',
                        processTokenizerName(str(node.argModifierTokenizer)),
                        node.argModifierTokenizer.func,
                        '    '
                    )
        children, refs = [], []
        # [Scan]: to prepare children and references for doc printout
        for child in node:
            # [Alt "ditto"]: to prepare dittoed children for doc printout
            if child.tokenList and isinstance(child.tokenList[0], DittoLabel):
                path = [x[0] for x in index.items() if x[1] == child.tokenList[0].tokenList[0]][0]
                refs.append((path, child.function))
            # [Alt]: to prepare children for doc printout
            else:
                children.append((child.name, child.function))
        # [Alt]: to write doc node children
        if node.name:
            outp.write('')
            outp.write('- *Child facts:*')
            # [Alt]: to do write doc node children
            if (children):
                # to do write doc node children
                outp.write('\n')
                # [Scan "children"]: to handle doc children
                for childName, function in children:
                    # [Opt]: to write doc child function
                    if (function and len(s := function.split('.')) == 2):
                        function = s[0]
                    # [Alt]: to format doc child function name
                    s = f'. {function}\n' if function else '\n'
                    outp.write(f'    - {childName}{s}')
            # [Alt]: to acknowledge no doc children
            else:
                outp.write(' (None)\n')
        # [Alt]: to write doc root facts
        else:
            outp.write('### Root facts\n')
            # [Scan]: to write doc root fact
            for i, (child, function) in enumerate(children):
                # [Opt]: to prepare to write doc root fact function
                if (function and len(s := function.split('.')) == 2):
                    function = s[0]
                # [Alt]: to format doc root fact function name
                s = f'. {function}\n' if function else '\n'
                outp.write(f'{i + 1}. {child}{s}')
        # [Opt]: to write doc references
        if (refs):
            outp.write('\n')
            outp.write('- *Available composite fact:*\n')
            # [Scan]: to format doc ditto reference
            for ref, function in refs:
                # [Opt]: to prepare to write doc reference function
                if (function and len(s := function.split('.')) == 2):
                    function = s[0]
                # to format doc reference function name
                s = f'. {function}\n' if function else '\n'
                outp.write(f'    - {ref}{s}')
        outp.write('\n')
        # [Msg]: to print graphic EBNF diagram
        printGraphicEbnf()

        childNum = 0
        # [Scan]: to print schema node child
        for child in node:
            # [Esc Once]: already visited
            if child in visited: continue
            childNum += 1
            # [Msg]: to report Protonabu schema under Label
            reportNode(child, visited + [child], index, ranks + [childNum])

    # [Opt]: to direct schema printout to the terminal
    if not outp:
        outp = sys.stdout
    # [Msg]: to report immediate directives header
    outp.write('### Immediate directives:\n\n')
    # [Opt]: to report immediate directives
    if schema.immediateDirectives:
        # [Scan]: to report immediate directive
        for directive in schema.immediateDirectives:
            outp.write(f'- {directive}\n')
        outp.write('\n')
    # [Msg; Alt]: to acknowledge no immediate directives in schema doc
    else:
        outp.write('(None)\n\n')
    # [Msg]: to report Protonabu schema under Label
    dummySchema = Label('')
    dummySchema.tokenList = schema.rootList
    # [Msg]: to report Protonabu schema under Label
    reportNode(dummySchema, [], schema.index, [])
