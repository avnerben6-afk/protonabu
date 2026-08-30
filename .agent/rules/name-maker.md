# NameMaker Utility Guide

The `NameMaker` singleton class (imported as `nameMaker` from `protonabu.util.stringUtil`) is the centralized naming facility in Protonabu. It handles formatting, abbreviation, magic-method translation, and namespace-aware uniqueness validation.

## Key Abstractions & APIs

### 1. Centralized Magic Method Translation
- **API**: `nameMaker.translateMagicMethod(methodName: str) -> str`
- **Purpose**: Translates Python magic/dunder methods into capability verbs.
- **Customization**: Uses `nameMaker.setMagicMethods(mapping)` to register domain-specific magic method mappings. Non-magic methods are automatically un-cameled (e.g., `doSomething` ➔ `do something`).

### 2. Namespace-Aware Uniqueness Validation
- **API**: `nameMaker.makeUniqueProgrammaticName(name: str, scopes: list = None, ref: Any = None, suffix: str = '', ignoreLast: str = '', capFirst: bool = True, isAcronym: bool = False) -> str`
- **Purpose**: Generates unique programmatic names within specified scopes.
- **Object Tracking**: Accepts a `ref` parameter. If a collision is found in the scope registries:
  - If `ref` matches the registered reference, it is treated as a safe re-registration/non-collision.
  - Otherwise, a numeric suffix (1, 2, 3, etc.) is appended to ensure uniqueness.
- **Registry Clearing**: Use `nameMaker.clearRegistries()` to clean up the namespaces between parsing sessions.

### 3. Trailing Preposition & Article Stripping
- **Purpose**: Removes trailing articles (`the`, `a`, `an`) and prepositions (`to`, `of`, `at`, `by`, `in`, `on`, `with`, `for`, `from`) during programmatic name generation and capability name shortening. This prevents awkward Infinitive/Definitive suffix constructs.
