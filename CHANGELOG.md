# Changelog

All notable changes to the **Protonabu** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.1] - 2026-09-13

### Added
- **Iterable Superpowers (`more-itertools`):**
  - Integrated `more-itertools>=10.0.0` as a core runtime dependency.
  - Re-exported foundational iterable utilities (`peekable`, `chunked`, `pairwise`, `one`, `partition`) directly from `protonabu.util` and `protonabu.util.loops`.
- **Fuzzy Name Resolution in `NameMaker`:**
  - Added `NameMaker.suggestSimilar(name, scope, limit, cutoff)` to support compiler diagnostics and "Did you mean?" suggestions on misspelled identifiers, leveraging `RapidFuzz` when present with a seamless fallback to standard library `difflib`.
- **Property-Based Testing (`Hypothesis`):**
  - Added `hypothesis>=6.0.0` under optional `test` extras in `pyproject.toml`.
  - Implemented automated invariant property tests in `testLoops` (testing `first`, `count`, `find` against arbitrary input distributions).
  - Implemented automated invariant property tests in `testStringUtil` (verifying `unquote`/`quote` roundtripping, `NameMaker` namespace uniqueness guarantees, and trailing article/preposition stripping).

### Changed
- **Loop Utilities Modernization:**
  - Refactored `protonabu.util.loops.first` to delegate directly to `more_itertools.first` with configurable default values while preserving backwards-compatible function signatures.

---

## [1.0.0] - 2026-08-29

### Added
- **Fact-Base Parsing Engine:**
  - Robust hierarchical indentation-aware parsing with `ProtonabuParser`, `ImportingProtonabuParser`, and `SnippetParser`.
  - Schema-driven grammar validation via `ProtonabuSchema` and `Label`.
  - Support for multi-line facts, ranked facts, and quoted strings containing arbitrary characters.
- **Snippet Adapters Subsystem:**
  - Generic `FactSnippetAdapter` and `SnippetAdapterSource` abstractions.
  - Standard snippet adapters for Markdown (fenced code snippets), JSON, and XML.
  - Pluggable `snippetAdapterFactory` registry for standard and contributed adapters.
- **Core Utility Package (`protonabu.util`):**
  - Exception hierarchy (`Error`, `InternalError`, `ParsingError`, `FactFileError`) preserving structured contexts, line numbers, and file references.
  - Traversal utilities (`iterUp`, `iterUps`, `find`, `findBehind`, `findNested`, `exists`, `findNoCase`, `firstValid`) with full DAG and cyclic-reference protection.
  - String utilities (`nameMaker`, `QuantityNarrator`, `DocDate`, `IdCounter`, `sanitizeProgrammaticName`, `pluralize`).
  - Progress reporting (`IProgressIndicator`, `DummyProgressIndicator`).
- **Testing Subsystem (`protonabu.testing`):**
  - Unified test framework (`BaseTestCase`, `TestData`, `test`, `getTestModules`, `runTestModules`).
- **Educational Site Generator Demo (`protonabu.demoApp`):**
  - Domain object model for books, chapters, sections, pages, and interactive presentation elements.
  - Parser for `.facts` lecture foil-set specifications.
  - Static HTML builder with modern CSS styling and mutual hyperlinking.
  - Combined multi-page PDF exporter.
- **Documentation & Design Specifications:**
  - Comprehensive `ProtonabuUserGuide.md` with complete architectural guide, grammar specifications, and walkthroughs.
  - Formal Nabu exported design fact-bases in `doc/exported/`.
