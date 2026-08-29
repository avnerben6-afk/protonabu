# Protonabu

*Open source infrastructure for authoring Domain-Specific Languages (DSLs), originally facilitating the Nabu Design Language.*

- **Author:** Avner Ben
- **Version:** 1.0.0
- **License:** MIT

---

## Overview

**Protonabu** is the self-contained parser and runtime substrate of the Nabu ecosystem. It provides:

1. **Fact Parsing & Schema Engine:** Hierarchical, indentation-aware fact-base parsing against dynamic BNF-like schemas (`ProtonabuParser`, `ProtonabuSchema`, `RawFact`, `TokenizedFact`).
2. **Snippet Adapters:** Bi-directional snippet conversion and round-tripping for multiple structured formats including Markdown, JSON, and XML (`FactSnippetAdapter`, `snippetAdapterFactory`).
3. **Core Utility Library:** Standardized naming conventions (`NameMaker`, `QuantityNarrator`, `DocDate`), hierarchy traversal utilities (`iterUp`, `iterUps`, `find`, `findBehind`, `findNested`), progress reporting (`IProgressIndicator`, `DummyProgressIndicator`), and typed structured exception hierarchies (`Error`, `InternalError`, `ParsingError`, `FactFileError`).
4. **Testing Infrastructure:** Common testing harness and runner for test discovery and regression test execution (`testing.py`).
5. **Educational Site Generator Demo:** A complete demonstration application that compiles `.facts` site descriptions into static HTML sites and multi-page hyperlinked PDF books (`SiteGenerator`, `SiteParser`, `pdfExporter`).

---

## Installation

```bash
pip install protonabu
```

Or for local development:

```bash
pip install -e .
```

---

## Running Tests

To run the complete test suite:

```bash
python programs/testAll.py
```

---

## Architecture & Interfaces

Detailed specifications and exported design interfaces are available in `doc/`:
- `doc/ProtonabuUserGuide.md` — Protonabu User Guide & Architecture
- `doc/NabuInCodeDocumentation.md` — Nabu In-Code Documentation Standards
- `doc/exported/` — Nabu design fact-bases and formal exported interface definitions
