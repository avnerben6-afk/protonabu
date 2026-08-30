# Nabu Documented Code Rules

**CRITICAL RULE:** In-code documentation follows a strict syntax called "Nabu Documented Code." It is **NEVER** free-text. This standard applies at all times when auditing, interpreting, or generating code documentation. There is always a standard way to document non-programmatic info—if in doubt, ask the user or refer to `doc/NabuInCodeDocumentation.md`.

## 1. Module Headers
Module headers must be strictly maintained and accurately attributed:
- **Author Block**: 
  - In standard project modules: `- Author: Avner Ben`
  - In generated modules: `- Author: <DEVELOPER>` (defaults to `Unknown`).
  - Must include a dated sub-bullet from document date types (e.g., `- Created: <DD-Mon-YYYY>`).
- **Generator Block** (If applicable):
  - In standard project files: `- Generator: <AI Model + Version>` (e.g., `Antigravity (Gemini 3.7 Flash)`).
  - Must include a dated sub-bullet. Use `- Generated: <date>` (from scratch), `- Injected: <date>` (added to existing source), or `- Improved: <date>` (punctual adjustments).

## 2. PRODUCT Documentation
PRODUCT-level documentation strictly belongs in an `addendum.nabu` file written in pure Nabu syntax, not as free-text code comments.

## 3. Reference Architecture
When writing or auditing Nabu structures, prioritize these references:
- **User Guide**: `doc/ProtonabuUserGuide.md`.
- **In-Code Documentation**: `doc/NabuInCodeDocumentation.md`.

## 4. Temporary Files
- **Sandbox Location**: Any temporary output, generated artifacts (e.g. from tests), or serialized structures (like `pickle` files) MUST be written to the `testArea/` directory located at the project root.
- **Git Hygiene**: Do NOT clutter the `src/` or `programs/` directories with temporary generated files. The `testArea/` folder is explicitly excluded from version control and should be used as the standard sandbox.

## 5. In-Code Documentation Guidelines
When generating or auditing in-code documentation, adhere to `doc/NabuInCodeDocumentation.md`:
- **Section 2.0.1** ("Naming hygiene for synthesized annotation text") for the rules on action/cause separation, ownership form, and punctuation stripping.
- **Section 7.2.1** ("Message"): Use `[Msg]` ONLY for calls to familiar methods/functions within the project. External standard library and infrastructure calls (e.g. `os.path.join`, `re.sub`, `time.mktime`, sys.exit) are considered local capabilities of the requirer and MUST NOT use `[Msg]`.
