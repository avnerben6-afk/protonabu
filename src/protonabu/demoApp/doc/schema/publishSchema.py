""" Module: publishSchema
    - Purpose: to act as a utility script to publish the Educational Site Generator schema
    - Author: Avner Ben
        - Created: 17-Apr-2026
    - Generator: Antigravity (Gemini 3.1. Pro)
        - Generated: 17-Apr-2026
"""

import os
from pathlib import Path

from nabu.protonabu.demoApp.siteParser import SiteParser
from nabu.protonabu.reportSchema import reportSchema

def main():
    """ to publish Educational Site Generator schema documentation
    """
    # [Msg]: to INITIALIZE Educational Site Parser
    parser = SiteParser()
    
    # [Opt]: to prepare output directory
    schemaDir = Path(__file__).parent
    os.chdir(schemaDir)
    
    docPath = schemaDir / "schemaDoc.md"
    print(f"Publishing schema to {docPath}...")
    
    # [Msg]: to generate schema report
    with open(docPath, "w", encoding="utf-8") as outp:
        reportSchema(parser.schema, outp)
        
    print("Publishing complete.")

if __name__ == '__main__':
    main()
