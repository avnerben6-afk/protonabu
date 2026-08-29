""" Module: Protonabu Raw Fact Test Data
    - Author: Avner Ben
        - Created: 4-Apr-2026
        - Improved: 24-Aug-2026
            - Prepared for release
    - Generator: Antigravity (Gemini 3.1 Pro)
        - Generated: 4-Apr-2026
"""

from .testing import TestData

testData: dict[int, TestData] = {
    1: TestData(
        title='single-line Raw Fact',
        testInput='INPUT [OPT; STATE]: EXPECTED "result" 32 [xxx "original" yyy; gvgvg \'77\' 7]',
        expectedOutput='INPUT [OPT; STATE]: EXPECTED "result" 32 [xxx "original" yyy; gvgvg \'77\' 7]'
    ),
    2: TestData(
        title='Raw Fact to over-long line',
        testInput='INPUT [OPT; STATE]: EXPECTED "result" 32 [xxx "original" yyy; gvgvg \'77\' 7]'.replace('OPTION;', 'OPTION "okojihygtyhiplpinu uihuhgygyg ijihhuhugug okokokokokook oplplplpl";'),
        expectedOutput='INPUT [OPT; STATE]: EXPECTED "result" 32 [xxx "original" yyy; gvgvg \'77\' 7]'.replace('OPTION;', 'OPTION "okojihygtyhiplpinu uihuhgygyg ijihhuhugug okokokokokook oplplplpl";')
        # Dynamic expected calculation handled in setUp for this specific case context
    ),
    3: TestData(
        title='Raw Fact from multiple-line Fact',
        testInput=['    INPUT [OPT; STATE]:', '    - EXPECTED "result" 32 [xxx "original" yyy; gvgvg \'77\' 7]'],
        expectedOutput='INPUT [OPT; STATE]: EXPECTED "result" 32 [xxx "original" yyy; gvgvg \'77\' 7]'
    ),
    4: TestData(
        title='multiline Raw Fact with comments',
        testInput=[
            ' // ignored comment 1',
            ' // ignored comment 2',
            '    INPUT [OPT; STATE]:', 
            '    - EXPECTED "result" 32 [xxx "original" yyy; gvgvg \'77\' 7] // comment part 1',
            ' // comment part 2'
        ],
        expectedOutput='INPUT [OPT; STATE]: EXPECTED "result" 32 [xxx "original" yyy; gvgvg \'77\' 7] // comment part 1 comment part 2'
    ),
    5: TestData(
        title='Raw Fact with rank',
        testInput='        INPUT [OPT; STATE]: EXPECTED "result" 32 [xxx "original" yyy; gvgvg \'77\' 7]',
        expectedOutput='        INPUT [OPT; STATE]: EXPECTED "result" 32 [xxx "original" yyy; gvgvg \'77\' 7]'
    ),
    6: TestData(
        title='Raw Fact with bad rank',
        testInput='        INPUT [OPT; STATE]: EXPECTED "result" 32 [xxx "original" yyy; gvgvg \'77\' 7]',
        expectedOutput='Error'
    ),
    7: TestData(
        title='Raw Fact with double slash inside double quoted string',
        testInput='PROPERTY [URL]: "https://example.com/a // b" [EXTERNAL "endpoint // not a comment"] // trailing comment',
        expectedOutput='PROPERTY [URL]: "https://example.com/a // b" [EXTERNAL "endpoint // not a comment"] // trailing comment'
    )
}

