---
description: How to correctly update semantic versioning and Git tags during Protonabu repository additions
---

# Protonabu Versioning Scheme Workflow

This workflow ensures the Protonabu project strictly follows semantic versioning combined with standardized Git tagging for releases and continuous integration.

## Protocol Before Committing Code

1. Verify what features or bug-fixes were introduced to determine the correct target version string (Patch, Minor, Major).
2. Run the automated `closeVersion` utility:
   ```bash
   .venv/bin/python programs/closeVersion.py <Major|Minor|Patch> -m "<Commit Message>"
   ```
- **Example (Patch bump)**:
  ```bash
  .venv/bin/python programs/closeVersion.py Patch -m "Clean in-code annotations in stringUtil"
  ```
- **Example (Dry Run)**:
  ```bash
  .venv/bin/python programs/closeVersion.py Patch -m "Clean in-code annotations in stringUtil" --dry-run
  ```
