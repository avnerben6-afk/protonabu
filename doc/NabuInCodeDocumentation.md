# Nabu Code-embedded Documentation
### Instructions for identifying, interpreting and generating Nabu-documentation embedded in Python code
By Avner Ben.


#### 1. Introduction
The Nabu in-code documentation serves the following purposes:
1. To allow extracting a Nabu snippet from the code mechanically. (E.g., using the "Nabu Python Extractor" program). Hence it follows a formal, machine-readable format.
2. To direct the implementing programmer how to complete a Nabu-code starter.
3. To enlighten and guide the maintenance programmer.

The Nabu documentation in a code module was either generated with the code by the Nabu Python code generator (TBD), inserted into the code manually by a human programmer, or either of the above, maintained and elaborated by a human programmer, (hopefully) in synch with the adjacent code.

Nabu-observing programmers - implementing and maintaining - are  expected to update Nabu in-code documentation to keep it in synch with the code, while still keeping it readable for the extractor program.

Nabu documentation is essential but not mandatory. The Extractor can figure out a default specification for most Nabu documentation that may - or may not - be sufficient. In fact, it will take a code file even if devoid of documentation. But some Nabu documentation is beyond the Extractor’s capabilities and had better be supplied by the user, if it is design-significant! The “status” items below distinguish between “automatic” documentation (that will be generated if missing), “manual” documentation (that will not be generated if missing) and “optional” documentation (nice-to-have documentation that is ignored by the Extractor).

Not all Nabu documentation is embedded in the code. Additional Nabu documentation package may be specified separately in a file by the name of “addendum.nabu” in the same folder. While the contents of this addendum specification is undefined, it is normally used for administrative and additional documentation (that either would clutter the code or has no obvious location in it, to circumvent the prospect of mis-documentation). The addendum is a proper snippet in the Nabu design language (rather than Python) whose syntax is beyond the present scope. Typical contents of the addendum file are Product (Python package) details, Use Cases, Use Case Scenarios, Scenario Points and Work Plan Milestone and Developer details.

#### 2. General guidelines
- Nabu does not support free-style documentation, let alone structured “info bullet” lists, under some selected items. Nabu syntax is based upon years of experience with real-world design and coding and is rich enough to cover all sensible code documentation needs. 

- Nabu documentation occurs in docstrings (module, class and method) and elsewhere, in commented lines above the respective programmatic entity (for example, above a conditioned block). 

  - Only single-hash (“#”) comments are read. Double-hash (“##”) comments are ignored by the Extractor. Hence, you can use double-hashed comments for non-Nabu content in order to hide it from the Extractor, as well as to prevent it from misleading the Extractor (for example, when immediately preceding or following legitimate Nabu documentation, to prevent them from mingling.

  - Nabu documentation is only interpreted when found in certain positions in the code, where it is expected. The Extractor first reads the code and then looks for adjacent documentation. Consequently, documentation that happens to be in the wrong position will be ignored!

- Nabu documentation occupies blocks of complete lines. Comments that trail a line of code are ignored.

- The names of Nabu facts (managed entities, such as product, part and capability) may contain spaces. (They are isolated from surrounding text by syntactical means). Nabu fact names may contain upper-case and lower-case letters, digits (except at the start), hyphens, spaces (reduced to one if consecutive), underscore and slash, except for the special case of slash surrounded by spaces, which is used elsewhere as name separator). As follows, Nabu fact names may not contain punctuation, tabs or special characters and may not span lines (unless otherwise indicated).

  - In addition to the above, capability names (only) may contain the less-than and greater-than symbols at a designated spot, delimiting a “substitution window” - see below.

- Nabu fact names are case-insensitive. We may say that two names in the documentation refer to the same Nabu fact if they match, case-insensitive.

- The following Nabu fact names (that are significant to in-code documentation) are unique (in the entire project documentation namespace): Product, Part and Capability. 

  - Nabu does not support local names, such as corresponding to the programmatic locally-unique names of inner function, inner class and inner package. To document such programmatic entities, qualify them (lexicographically) by their owner or find the means to make them unique!  

- Nabu keywords and special and reserved words are preferably (but not necessarily) indicated in Nabu by all-caps.  *Example:*

  > ````python
  > to INITIALIZE Requirement Argument set
  > ````

- Free text (that is not a keyword, reserved name, or managed entity) is normally surrounded by double quotes.  *Example:*

  > ````python
  >             # [Opt "Parameter"]: to find pending argument for actual argument
  >             if forParameter:
  >                 argEntry = getArgByName(forParameter, isPositional = False)
  > ````

- Names and quoted text - with the exception of "capability" name - are normally capitalized.  (See above example).

- “Conditions ”(such as escape, option and loop conditions) used in Nabu documentation are normally quoted free text. An exception is “Capability” name (see below). When the condition evaluates to capability name, it must be a valid capability name although (functioning as as text). 

- Nabu documentation does not use comma for separation. When commas or other punctuation appears in free text, they are interpreted as part of the text. Nabu facts are usually specified one per line. The only separator used in Nabu documentation is the semicolon. Some cases of multiply-specified facts (such as multiple condition keywords) are separated by semicolons.  

- Nabu documentation does not use round brackets for segregating sub-items. It uses only square brackets. When round brackets appear in free text, they are interpreted as part of the text. 

#### 2.0.1. Naming hygiene for synthesized annotation text

When the Extractor (or an AI completing code) synthesizes annotation text from programmatic constructs, the following naming rules apply:

- **Action/cause separation.** A capability name shall consist of the *action taken* only. The *cause* (the condition under which the action occurs) belongs in the condition tag argument (the quoted text within square brackets), not in the capability name itself.

  *Wrong:*
  > ````python
  > # [Opt]: to update genNum when owner of gener equals aProduct
  > ````

  *Correct:*
  > ````python
  > # [Opt "owner of gener equals aProduct"]: to update genNum
  > ````

- **Ownership form for dot-notation.** Programmatic dot-notation expressing attribute access must be translated to natural-language ownership form, reversing the order. E.g., `gener.owner` → `owner of gener`, `self.dates` → `dates of self`, `a.b.c` → `c of b of a`.

- **No punctuation in synthesized names.** All synthesized annotation text (capability names, condition arguments, scanning labels) must be free of periods, brackets, parentheses, and other punctuation. Operators are translated to words (`==` → `equals`, `!=` → `not equals`, `>` → `greater than`, etc.). The `sanitizeProgrammaticName` utility in `stringUtil.py` implements these transformations automatically.

- **Un-cameling.** CamelCase identifiers are split into space-separated words. E.g., `currGener` → `curr Gener`, `aProduct` → `a Product`.

#### 2.1. Selective Extraction — The `[Ignored]` Prefix

Most documented fact may be marked for suppression by placing `[Ignored]:` as a bracket-prefix on its documentation line. The extractor will silently skip the marked fact and all of its children — no Nabu facts are emitted for the ignored scope.

- The keyword is **case-insensitive**: `[ignored]`, `[Ignored]`, and `[IGNORED]` are all equivalent.

- `[Ignored]` may appear alone or as part of a **prefix group** (semicolon-separated), e.g.:

  > ````python
  > # [Alt; Ignored]: to fallback when service unavailable
  > if not service:
  >     fallback()
  > ````

  When combined with another condition tag in a prefix group, `[Ignored]` takes full priority — the **entire construct** (including all branches, body, and children) is suppressed. The co-present tag (e.g., `Alt`) is **not** emitted. Rationale: the extractor must never produce incomplete or misleading logic by emitting one arm of a conditional without the others.

- **Scope rules** (depth-wise suppression):

  | Fact | Suppression extent |
  |---|---|
  | Module (file docstring) | Entire file — no `MODULE` or `IMPLEMENTATION` entry emitted |
  | Part (class docstring) | Entire class body — no `PART` entry or child capabilities emitted |
  | Capability (function docstring) | Entire function body — no `CAPABILITY` entry or child requirements emitted |
  | Requirement (comment above statement) | The statement and its subordinate block — no `REQUIRES` entry or nested requirements |

- Status: **voluntary**. The extractor never infers `[Ignored]` automatically.

*Example — module suppression:*

> ````python
> """ [Ignored]: Module: Experimental Prototype
>     - Author: Someone
> """
> ````

*Example — capability suppression:*

> ````python
>     def legacyBridge(self):
>         """ [Ignored]: to call legacy subsystem
>         """
>         …
> ````

*Example — requirement (for-loop) suppression:*

> ````python
>         # [Ignored]: to iterate over debug entries
>         for entry in debug_log:
>             process(entry)
> ````


#### 2.2. Compact Generation Hint — `[COMPACT]`

The Nabu code generator may be directed to emit **compact** code — list/set/dict/generator comprehensions for scanning constructs, and chained ternary-if for alternative sequences — by means of the `COMPACT` label-modifier on `SCANNING` and `CRITERION` facts respectively.

**SCANNING — compact modifier:**

The modifier is appended (via semicolon) to the existing label-modifier slot:

| Modifier | Generated form |
|---|---|
| `[COMPACT]` or `[COMPACT LIST]` | List comprehension `[expr for x in seq]` |
| `[COMPACT SET]` | Set comprehension `{expr for x in seq}` |
| `[COMPACT DICT]` | Dictionary comprehension `{k: v for x in seq}` |
| `[COMPACT GENERATOR]` | Generator expression `(expr for x in seq)` |

`LIST` is the default — `[COMPACT]` and `[COMPACT LIST]` are equivalent. The restorer always emits `COMPACT` alone for the LIST case (no redundant suffix).

*Example — hand-authored Nabu requesting a set comprehension:*

> ````
> REQUIRES: to collect unique tags
>     SCANNING [COMPACT SET]: "tag list"
> ````

**CRITERION — compact modifier:**

The `CRITERION` fact (first-alternative marker) accepts a `[COMPACT]` label-modifier to indicate a chained ternary-if expression. When present, `CRITERION` **must** always be emitted, even when the criterion text is empty, so the modifier has a carrier:

*Example — hand-authored Nabu requesting ternary-if:*

> ````
> REQUIRES: to decide label
>     ALTERNATIVE: "value is positive"
>         CRITERION [COMPACT]: "value > 0"
> ````

**Extractor automatic inference:**

The extractor infers compactness from the programmatic construct automatically — no explicit `[Compact]:` tag is needed in the Nabu-doc:

- When the annotated code uses a **comprehension** (`list_comprehension`, `set_comprehension`, `dictionary_comprehension`, or `generator_expression`), the extractor sets the corresponding compact type on the `SCANNING` condition.
- When the annotated code uses a **ternary-if** (`conditional_expression`) with multiple arms, the extractor always emits `CRITERION [COMPACT]` for every arm.

**Language-agnostic semantics:**

Specifying `COMPACT` for a language that does not support the compact form (e.g., Java, C++) is **not an error**. The code generator will silently fall back to conventional code (`for` loop or `if/elif/else`) and ignore the hint.

**Using COMPACT to express improvement intent:**

A developer may explicitly mark `[COMPACT]` on a Nabu fact even when the current source code still uses a conventional `for` loop or `if/elif` — for instance, when documenting third-party code for future refactoring, or when the design calls for a comprehension that has not yet been implemented.

In this scenario, the next code-generation cycle will produce the compact form in the generated output, which is the intended effect. However, if the source file is then refreshed by the Nabu-doc injector, the injected documentation will *describe the compact intent* while the code below it remains conventional. This **cognitive dissonance** between the documented intent and the actual code is the developer's responsibility to resolve — either by updating the code to match, or by removing the `[COMPACT]` modifier.

- Status: **automatic for extraction** (inferred from node type); **voluntary for hand-authored Nabu** (explicit `[COMPACT]` on any SCANNING or CRITERION fact).


#### 3. Module documentation
- Location: module docstring. (Multiline string at top of module).
- The keyword “Module”, followed by colon, followed by module name. By default, the module name may be extracted from the current file name, word-separated.
- The module header may be detailed by info-bullet blocks up to three levels deep:
  - Contributor line. A contributor keyword, followed by colon, followed by name. The valid contributor keywords are: `"Author"`, `"Producer"`, `"Generator"`, and `"Auditor"`.
    - **The 3-Tier Contributor Hierarchy**: Modern Nabu-doc projects recognize three distinct roles in the development lifecycle:
      1. **Author** (Human): The human developer/designer. Event types: `Created`, `Improved`, `Fixed`, `Revised`, `Reviewed`.
      2. **Producer** (AI Orchestrator): The AI agent supervising production, audit, and round-trip lifecycle (e.g., `Antigravity`). Event types: `Produced`.
      3. **Generator** (Compiler): The code-generation or compilation engine emitting code (e.g., `Nabu`). Event types: `Generated`, `Injected`.
    - The contributor entry may be detailed by date-entry blocks. The date-entry header line consists of an event-type keyword, followed by colon, followed by date, normally in the format dd-MMM-YYYY. The valid event types are: `"Created"`, `"Produced"`, `"Generated"`, `"Injected"`, `"Improved"`, `"Fixed"`, `"Revised"`, and `"Reviewed"`.
      - A date entry may be detailed by headless bullets - label-less free-text lines, detailing the event, if not obvious from the above.
        - Headless bullets may not contain floating slash (“ / ”), as this is used internally to separate them. But this is not checked by the extractor. A headless bullet that contains a floating slash will appear in the visuals as two lines!
  
- Status: automatic. If not specified by the user it will be generated by the Extractor, using the file name for module name.

*Example:*

> ````python
> """ Module: Nabu API Module
>     - Author: Avner Ben
>         - Created: 13-Mar-2025
>     - Producer: Antigravity (Gemini 3.1 Pro)
>         - Produced: 06-Jun-2026
>     - Generator: Nabu 0.9.5
>         - Generated: 06-Jun-2026
> """
> ````


#### 3.1. Recursive Import Documentation
- Location: Comment line immediately preceding a Python `import` or `from ... import` statement.
- Keyword: `[Additional]`.
- (Semantics: Indicates that the Extractor should recursively follow this import and parse the target module for Nabu-documentation. By default, the Extractor only parses the module(s) specifically designated on the command-line. This directive allows building a comprehensive documentation set from nested project dependencies while avoiding extraneous third-party or infrastructure modules).
- Status: manual. The Extractor does not read imported modules without this explicit directive.

*Example:*

> ````python
> # [Additional]
> from ..dl2View.std.projectTreeView import projectTreeView
> # [Additional]
> from ..dl2View.std.projectTreeView.projectTreeView import MenuTree
> ````

#### 4. Class documentation
- Location: class docstring.

- The name of the corresponding Nabu "part". 
  - By default, inspired by the class name, word-separated. User-defined part names may contain some additional information (compared with the bare class name), or bear no resemblance at all. The last is especially true for “polymorphic” parts that follow a strict pattern that has no immediate programmatic mapping. *Example:*
  
    > ````python
    >     class Entry:
    >         """ Polymorphic View Entry
    >         """
    > ````
  
- May be followed by descriptive info-bullets, one per line. 
  - An info-bullet consists of hyphen, followed by name (one or more words), followed by colon, followed by free text, optionally terminated by period (which is not part of the text).

  - An info-bullet may span multiple lines, usually aligned.

  - In addition, an info-bullet may be followed by one or more indented nameless sub-bullets, one per line, each consisting of hyphen, followed by free text. *Example:*

    > ````python
    > class TokenListIterator:
    >     """ Token List Iterator.
    >         - Purpose: to traverse tokenized fact, retaining the current label.
    >         - Motivation: to add state to structured Python iteration
    >     """
    > ````

- Status: automatic. If not specified by the user it will be generated by the Extractor.
#### 5. Method/function documentation
- Location: Method docstring.

- Status: automatic. If not specified by the user it will be generated by the Extractor.

- The name of the corresponding Nabu "capability", optionally preceded by definitive specification (described below). *Example:*
  > ````python
  >     def getVisualConfigOptions(self, visualName: str) -> Visual.Configuration:
  >         """ to get Visual View configuration options
  >         """
  > ````

  - A Nabu capability name consists of the word "to", followed by a strong verb, followed by free text.
    - A capability name often (but not necessarily) contains the name of its part, or a short form of it (because, in object-oriented programming, a method is there to do something to an object of its class).
    - A Nabu name should be concise and as short as possible, while still descriptive and readable. A good capability name is up to 7 words. Capability names of up to 12 words are tolerated. Beyond that is considered bad practice.
    
  - Special capability names:
    - Some "Designated" capability names contain one of the following reserved verbs, normally emphasized in all-caps:
      - "to INITIALIZE …" - Python constructor method (`__init__`).
      - "to FINALIZE …" - Python destructor method (`__del__`).
      - "to TRAVERSE …" - Python generator method (`__iter__` / `yield`).
      
    - **Strict Restriction on Reserved Designated Verbs**:
      - Reserved designated verbs (`INITIALIZE`, `FINALIZE`, `TRAVERSE`, `ENTER`, `EXIT`) are strictly restricted to their designated language mechanisms (e.g. `to INITIALIZE` for class constructors, `to TRAVERSE` for generators/iterators).
      - **NEVER** use `to initialize` (or any other designated verb) to document non-constructor operations, primitive variables, or non-user-defined type setups (such as creating/seeding a dictionary entry, list, or mapping key). For non-constructor setup, select alternative verbs such as `setup`, `create`, `seed`, `prepare`, `start`, or `reset` (e.g., `# [Opt]: to setup keyword entry`). 
    
      - For a "super-part" (Python super-class), the substitution window contains the word "SUBSTITUTE", possibly (but rarely) followed or preceded by one or more words. In the following example, the name of the abstract superclass is “Canvas”
    
        > ````python
        > # to begin rendering on <SUBSTITUTE> Canvas
        > ````
    
      - For a "sub-part" (Python sub-class), the substitution window contains the name of its part (or part of it, where the rest of it either trails or precedes the substitution window).In the following example, the name of the abstract superclass is “HTML Text Canvas”
      
        > ````python
        > # to begin rendering on <HTML Text> Canvas
        > ````

- By default (in the lack of proper Nabu documentation), a capability name may be generated by word-separating the method name, preceded by "to". (Assuming the imperative “procedural paradigm”. where the first word embedded in the function name is a strong verb). *Example:*

  > ````python
  >     def getVisual(self, visualName: str, factName: str, factType: str='')-> str:
  >         """ to get Visual
  >         """
  > ````

- A capability header may be followed by dataflow specification special bullet-info items, one per line - namely: “Input” and “Output”. The dataflow keyword may be followed (before the colon) by dataflow modifiers in square brackets (separated internally by semicolon, if more than one): “State” and “Opt”.

  - The dataflow modifier “State” indicates that the dataflow does not correspond to a formal parameter (in the case of function), but rather alters - or draws upon - program state. For example, to indicate some aspects of “Design By Contract”. *Example:*

    > ````python
    >     def generate(self):
    >         """ to generate Nabu static site
    >             - Output [State]: Folder system implementing the Project Tree view 
    >               with submenus as folders and visuals as pages
    >         """
    > ````

  - The modifier “Opt” indicates that the dataflow is optional, optionally followed by the default value or new-state, as free text. A typical default value is “none”, where the optionality of the argument is indicated by the platform-specific null value. *Example:*

    > ````python
    >             """ to judge the current Span Tree for complexity
    >                 - Input [Opt "None]: Candidate order and current complexity
    >             """
    > ````

- “Input” may alternatively appear as info-bullet above the argument in the function header, when the function header spans multiple lines, with each argument in a separate line. In the same vain, “Output” may appear last withing the argument-list brackets, thus expanded. 

  - Nabu does not support output or input and output formal parameters.

  *Example:*

  > ````python
  > 
  >     def find(
  >         self,
  >         # - Input: Name of object to find
  >         name: str,
  >         # - Input: Type of object to find              
  >         objectType: type,
  >         # - Input: Error when type mismatch       
  >         isMustConform: bool=True 
  >         # Output [Opt None]: the object by that name and type
  >     )-> Optional[Any]:          
  >         ''' to find design fact by name in the project namespace
  >         '''
  > ````

- The argument descriptor may contain the separator ‘–’ (double hyphen), separating the object transferred from its required state, where applies. This information is used by Nabu to calculate “data coupling”. *Example:*

  > ````python
  >         """ to get DL Model-View creator
  >             - Output [State]: View extension module -- loaded
  >             - Output [State]: View -- cached in Fact
  >         """
  > ````

- A programmatic tuple-parameter may optionally be Nabu-documented by its constituents, one per line, ignoring the fact of the tuple. *Example:*

  > ````python
  > 
  > ````

- The special capability info-bullet “Definitive”, with (only) one of the values “Part”, “Product”, “Project”, or “None”. This is used to arrange meaningful capability hierarchies in business-oriented reports. In addition, the special capability info-bullet “Title”, followed by capability name gives an alternative, more palatable name to the capability, for the same purpose. *Example:*

  > ````python
  >         """ to begin rendering on <HTML Text> Canvas
  >             - Definitive [Part]
  >             - Title: to render HTML Text Visual reduced to text primitives
  >         """
  > ````

#### 5.1. Composite dataflow and implementation mappings

Nabu supports documenting composite dataflow items directly under `Input` and `Output` annotations. These are denoted by indented sub-bullets labeled with the keywords `Contains`, `IMPLEMENTATION`, and `CONTAINS`.

- **Flat semantic elements**: Use `Contains:` followed by free text (optionally quoted) representing semantic sub-elements underneath `Input` or `Output`.
- **Hierarchical implementation mappings**: Use `IMPLEMENTATION [<CONTAINER_TYPE>]: "<implementation_name>"` (e.g. `IMPLEMENTATION [MAPPING]`) followed by nested, indented `- CONTAINS [<TYPE>]: "<field_name>"` sub-bullets to describe exact nested container and mapping structures (such as `dict[str, dict[str, list]]`).

*Example:*

> ````python
>     def getTransferable(self) -> dict[str, dict[str, dict[str, Any]]]:
>         """ to retrieve all non-machine-specific configuration for zip export
>             - Output: "transferable configuration"
>                 - Contains: "subsystem"
>                 - Contains: "subject"
>                 - Contains: "item"
>                 - Contains: "value"
>                 - IMPLEMENTATION [MAPPING]: "transferableConfiguration"
>                     - CONTAINS [str]: "subsystem"
>                     - CONTAINS [MAPPING]: "subjectAndItems"
>                         - CONTAINS [str]: "subject"
>                         - CONTAINS [MAPPING]: "itemAndValue"
>                             - CONTAINS [str]: "item"
>                             - CONTAINS [Any]: "value"
>         """
> ````

**Extractor Behavior and Synthesizing Defaults**

The Nabu code extractor strictly interprets the Nabu-doc as the literal design intent. It uses the `Contains` and `IMPLEMENTATION` elements to form `CONTAINS` children underneath the extracted dataflow node in the Nabu syntax. 
- The extractor does **not** validate the number or type of the `Contains` items against the actual programmatic type hint (e.g. `tuple[int, str, bool]`).
- If there are fewer `Contains` statements than type hint elements, the extractor **will not** synthesize default dataflow items to fill the gap. Nabu dataflows are treated as deliberate design decisions rather than a strict 1:1 map of the physical structure; omitting some elements from the documentation implies they are not design-significant.
- Conversely, specifying too many `Contains` items compared to the programmatic hint will result in all of them being extracted. Nabu assumes you are declaring design structures that may not perfectly reflect the current implementation. Structural limits and warnings for type mismatches belong to the design-validation phase (the Nabu Parser or `domBuilder`) and not the code extractor.

#### 6. Functional escape documentation

- Location: Comment above an if statement (or some other statement types specified below) followed by a block of code featuring "return", "continue", "break", or exception raising.
  - Other - less frequent - locations of functional-escape documentation are above "except" statement, above "else" statement, and above match final '_' statement.

- Consists of the keyword 'Esc', optionally followed by a modifier — both enclosed in square brackets — followed by colon, followed by the *reason* for escaping as free text (normally within double quotes). The text after the colon is **never** a capability or requirement — it is a description of the escape cause.
  - Escape modifiers: strictly one of 'DONE', 'ONCE', 'IGNORED', 'EXHAUSTED', or 'ERROR', or alternatively, an active argument (a name conforming to the capability form, i.e. starting with 'to', specifying the capability used to decide the escape). No other free text may follow the 'Esc' keyword inside the brackets. The escape modifier may be quoted.
  
  - The reason (following colon) is free text describing why the escape occurs. For `[Esc "Error"]`, this is typically the error type and/or message (e.g., `"KeyError"` or `"Invalid output folder"`).
  
  - If the escape block contains cleanup logic (one or more capability-requirements before the `return`/`raise`/`continue`), the cleanup requirements are documented *below* the escape annotation, above the imperative code — just like normal requirements.
  
    - Nested functional escape (I.e., functional escape from within the block of code under a functional escape) is not supported as of now.
  
  - Possible escape modifiers:
  
    - "Esc". (Semantics: premature termination, leaving the objective of the block or method unsatisfied. The escape is used in this case to avoid the error of tacitly relying on a broken state in the code that follows). *Example:*
  
      > ````python
      >         # [Esc]: end of file
      >         if self.curStart == len(self.lines):
      >             self.curEnd = self.curStart
      >             return
      > ````
  
    - The escape may be followed by free text reason, or the special reason “This time”, corresponding to a programmatic “continue” below. *Example:*
  
      > ````python
      >                 # [Esc "Once"]: "Not root"
      >                 if ' / ' in menuItem.path or menuItem.visualName: continue
      > ````
  
    - "Done". (Semantics: premature termination, where the objective of the block has already been satisfied by that point). The archetypal case is escape with the desired result from the loop in a search function. *Example:*
  
      > ````python
      >             # [Scan child entries]: to evaluate Functionality View node
      >             for childEntry in entry.entries:
      >                 # [Esc "Done"]: found
      >                 if result := walk(childEntry): return result
      >             return None
      > ````
  
    - "Ignore". (Semantics: either of the above, but the block is not terminated nevertheless). Rarely used, but valid (although the block of code below the documentation does not feature the escape behavior specified above). *Example:*
  
      > ````python
      >                 try:
      >                     child = self.index[part.getName()]
      >                 # [Esc "Ignore"]: not in index
      >                 except KeyError:
      >                     # to collect nested part
      >                     self.index[part.getName()] = (child := self.Entry(part))
      > ````
  
    - "Error". Reserved to when the block below either raises an exception or is already an exception handler (Python “except”). By default, the condition is extracted from the error message (the argument to the exception constructor, if available, stripped of unprintable characters and formatting instructions for statically-unavailable content). 
  
      - The descriptive error-escape text is recommended to be comprehensive, including context, because it is used in a separate audit-related report.
      - The error may be followed by argument modifier, specifying the error type, optionally  followed by double hyphen and error message, all quoted. 
  
      *Example:*
  
      > ````python
      >                 # [Esc "Error"]: "Invalid ouput folder" ["Error - Invalid output folder"]
      >                 elif not outFolder.is_dir():
      >                     raise Error('Invalid output folder', [('Given', str(outFolder))])
      > ````
  
    - Active argument. The capability used to decide the escape. *Example:*
  
  
    > ````python
    >      # [Scan child entries]: to evaluate Functionality View node
    >          for childEntry in entry.entries:
    >              # [Esc"to TRAVERSE child entries"]: found
    >              if result := walk(childEntry): return result
    >          return None
    > ````
  
    - “Exhausted”
      - Unconditional “return” at the end of a function or block that contains functional escapes. The archetypal case is a search function with a scan block with “Escape Done”.
      - The final `else` or `match _` in an alternative list that has functional escapes.
  
  - Status: automatic. If not specified by the user it will be generated by the Extractor.
  

#### 7. Capability-requirement documentation

* Location: Above code block.

* Consists of a capability name, optionally preceded by requirement condition. *Example:*

  > ````python
  >         # to skip position to beginning of footnotes
  >         self.curEnd += 3
  > ````
  
  * In case of function call (the condition “Msg”), the existence of the capability (elsewhere in this or other code) is not validated. 
  
  * A long capability-requirement header (typically due to condition with a long reason) may span multiple lines, broken after the colon. *Example:*
  
    > ````python
    > # [Scan "to collect available Scenario Points in the current requirement"]:
    > #     to expand possible Scenario Point
    > 
    > ````
  
  * In case the code below consists of a Nabu-documented (rather than platform built-in) function call, the requirement normally cites that capability. (By default, a capability name may be extracted from the programmatic function name - see “Capability”, above). *Example:*
  
    > ````python
    >         def walk(nodes: list[MenuTree.MenuItem]):
    >             """ to TRAVERSE Menu subtree hierarchical structure
    >             """
    >             # [Msg; Scan]: to yield node and subtree
    >             for node in nodes:
    >                 yield node
    >                 # [Msg; Scan]: to TRAVERSE Menu subtree hierarchical structure
    >                 yield from walk(node.children)
    > 
    >         # [Msg; Scan]: to TRAVERSE Menu subtree hierarchical structure
    >         yield from walk(self._rootNode.children)
    > 
    > ````
  
    * The required capability may refer to a function call that is embedded in the programmatic expression below, ignoring the whole of the expression, for semantic reasons. (E.g., the rest of the expression may be dismissed as insignificant wrapper). *Example:*
  
      > ````python
      > todo...
      > ````

- Capability-requirement documentation may also contain user–defined info bullets, Typically “Intent”, “Reason”, etc. *Example:*

  > ````python
  >         # to uppercase name for registration
  >         # - Intent: to make name registration case-insensitive
  >         name = name.upper()
  > ````

- Status: manual, except for conditional blocks. Individual code lines may be left undocumented (even when containing function calls) and will be ignored by the Extractor. However, the documentation of conditional blocks of code, if not specified by the user, will be generated.

##### 7.1. Requirement condition documentation

Consists of a keyword within square brackets, with the keyword optionally followed by free text describing the reason, normally quoted, followed by colon, followed by capability name. The capability  specifies the function-call, block of code, expression below, or the relevant part of the latter.

- These are the condition keywords: “Msg”, “Scan”, “Rpt”, “Opt”, “Alt”, “Crit”, and “Ctxt”.

- The semantics of the reason following the condition keyword depends upon the specific keyword. It is normally free text, but may also specify an “active condition” - a capability (in which case it must form a valid capability name). In the case of message (function call), the existence of the corresponding function - Nabu-documented or otherwise - is not verified (because it may exist beyond the scope of the current documentation, such as in a module that we , for some reason, do not read). 

- Nested conditions may be concatenated, when their content may be reduced programmatically to a single expression (rather than a full block of code), ignoring functional escape (because it is considered part of the control construct). In this case, the condition keywords (and their reasons, if present, appear above the top code line, separated by semicolon). *Example:*

  > ````python
  >         # [Scan; Scan]: to cut-out port in Wire Box
  >         for side, mess in enumerate(self.mess):
  >             for socket in mess:
  >                 socket.box.addPort(socket, side)
  > ````

  - This feature is characteristic of list and other comprehension. *Example:*

    > ````python
    >             # [Scan; Scan]: to collect imported parts in Association Diagram
    >             importedParts = [y for x in imported.items() for y in x[1]]
    > ````

- A capability-requirement may be followed by the reserved special info-bullets “Using”, “Delivering” and “Giving”, followed by colon, followed by argument text. These document the use of arguments. “Using” normally refers to formal function arguments, and “Giving” normally refers to the variable that takes the value of function-returned argument. “Delivering” refers to the value that accompanies a “return” statement (on the called function side) and is less frequently used. 

  - Requirement arguments apply to any capability-requirement (including such that do not involve function calls).
  - “Using” may also appear above the argument in the function-call, if the function call is divided to multiple lines, with each argument in a separate line. Otherwise (when the “Using” clause is part of the requirement, it is assigned by position, unless explicitly matched to formal parameter using the “For” modifier - see below.) *Example:*

  > ````python
  >         self.drawRectangle(
  >             # - Using: to INITIALIZE Rectangle
  >             Rectangle(
  >                 # - Using: to INITIALIZE Point
  >                 Point(
  >                     # - Using: shade offset
  >                     rect.origin.x + offset.x, rect.origin.y + offset.y
  >                 ), 
  >                 rect.h,
  >                 rect.w
  >             ),
  >             # - Using [For "pen name"]: Shade pen name
  >             shadePenName,
  >             # - Using [For "brush name"]: Shade brush name
  >             shadeBrushName
  >         )
  > ````

  -  Active argument text (consisting of capability name) is allowed (in case the corresponding programmatic argument is a function call), - see example above.

  - A programmatic tuple-argument may also be Nabu-documented by its constituents, one per line, ignoring the fact of the tuple. *Example:*

    > ````python
    > 
    > ````

  - The “Using” keyword may be followed (before the colon) by argument modifier “For” in square brackets, followed (within the square brackets) by optionally-quoted free text, assigning the argument to an input dataflow (formal parameter) of the capability by that name.  *Example:*

    > ````python
    >               # to add Console menu option
    >               menu.addOption(
    >                   unCamel(config.index[i]), 
    >                   # - Using [For "handler"]: "to execute Visual Option Setter"
    >                   optionSetter.__call__, 
    >                   None
    >               ) 
    > ````

  - **External Dataflow Hooks (`Source` / `Sink`):** Dataflow bullets (`Using`, `Giving`, `Delivering`) may be followed by an indented sub-bullet specifying the external agent/system entity liaison (`- Source: <extern>` for `Using`, `- Sink: <extern>` for `Giving` and `Delivering`). These sub-bullets are extracted into `SOURCE` and `SINK` facts under the parent dataflow fact in the Nabu fact-base. *Example:*

    > ````python
    >               # to process payment
    >               # - Using [For "token"]: payment_token
    >               #   - Source: Payment Gateway
    >               # - Giving [For "receipt"]: transaction_receipt
    >               #   - Sink: Customer Audit DB
    >               # - Delivering [For "status"]: response_status
    >               #   - Sink: Merchant Webhook
    >               process_payment(payment_token)
    > ````

Status: automatic. If not specified by the user it will be generated by the Extractor. For example, a (condition-less) capability-requirement documentation above a for-loop will be adorned automatically with the “Scan” attribute by the Extractor. 

##### 7.2.1. Message

The naked keyword “Msg” (not followed by descriptive text). Used when the required capability is a **familiar capability** implemented by a function or method invocation within the project (to call). Normally first in sequence. *Example:*

> ````python
>         # [Msg]: to find next embedded DL window
>         self.next()
> ````

- **Familiar vs. Infrastructure:**
  - **Familiar project calls:** A call to a function or method defined within the project or part (such as a domain helper, constructor, or internal method) is documented with `[Msg]`.
  - **Infrastructure method calls:** Standard library, OS, and third-party library calls (such as `os.path.join()`, `os.path.dirname()`, `re.sub()`, `sys.exit()`, file I/O `write()`, etc.) are considered **local capabilities of the requirer**, because external infrastructure does not belong to the Nabu project domain model. Therefore, they represent inline actions and **must NOT** be prefixed with `[Msg]`. Document them as standard un-prefixed requirements (e.g. `# to create path to PlantUML diagram`).

- Status: informational. Ignored by the extractor. 

##### 7.2.2. Scanning condition documentation

- Location: above for-loop block header, above list/dict/set/generator comprehension and above “yield from”.

- Condition keyword: “Scan”. 

- Condition reason (optional): the name of the container or stream being scanned. 

  - Often inspired by the name of a variable in the code above or a container member, word-separated. *Example:*

    > ````python
    >     dlSection: list[Line] = collectLines()    
    >     # [Scan]: to write unformatted Line
    >     for line, isAnnotated in dlSection:
    > ````

  - May also be “active” - the capability name of the generator-function called below. *Example:*
  
    > ````python
    > # [Scan "to TRAVERSE pending snippets"; Scan "to TRAVERSE snippet lines"]: 
    >     # to retrieve current snippet line
    >     for pendingExpand in iterChildren(fact.rank):
    >         yield from pendingExpand
    > 
    > ````
##### 7.2.3. Repeated condition documentation
- Location: above while-loop block header.

- Condition keyword: “Rpt”. 
- Condition reason: “While”, “Until”, or “Times”, optionally followed by free text. *Example:*

> ````python
>         # [Rpt "While temp model objects exist"]: to erase fake capabilities
>         while self.tempModelObjects:
>             tempCapability = self.tempModelObjects.pop()
>             # to disassociate capability from Part
>             with suppress(ValueError):
>                 tempCapability.owner.giveUp(tempCapability)
> 
> ````

*Example:*

> ````python
>             # [Rpt "Times 5"]: to delete the temporary Graph-viz snippet
>             for i in range(5): 
>                 if not fileName.exists(): break
>                 try:
>                     imgFileName.unlink()
>                 except:
>                     time.sleep(.001)
> 
> ````

##### 7.2.4. Optional condition documentation
- Location: above if-block header that is not followed by an elif/else-block.

- Condition keyword: “Opt”. 
- Condition reason: Free text. May also be “active” - capability name corresponding to function call within the programmatic condition below.

*Example:*

> ````python
>             # [Opt]: to skip floating comment in DL file
>             if lines[0].lstrip().startswith('//'):
>                 lines.pop(0)
> 
> ````

- Alternatively, a programmatic if-headed block may be rather documented by functional escape - see above.

##### 7.2.5. Alternative condition documentation
- Location: above case-block, and above if-block header that is followed by an elif/else block, and above its elif and else blocks.
- Condition keyword: “Alt”. 
- Condition reason (optional): optionally-quoted free text, specifying the inspected value. 
- Nabu has no “otherwise” default selection. All alternatives, including the last in sequence, must be documented. 

*Example:*

> ````python
>             # [Alt]: to execute DL command-line visual request
>             if self.visualProps:
>                 executeCommand()
>             # [Alt]: to select from the Design Language main menu
>             else:
>                 selectFromMainMenu()
> ````

*Example:*

> ````python
>         match fileName.suffix:
>             # [Alt "familiar file type"]: to open visual file in web browser
>             case '.html' | '.svg' | '.png':
>                 webbrowser.open(f'file://{fileName.resolve().as_posix()}')
>             # [Alt "Unsupported visual format"]: to print reject message
>             case _:
>                 print(f'File type "{fileName.suffix}" not supported yet!')
> ````

- Alternatively, a programmatic if-headed block may rather be documented by functional escape - see above.
- Alternatively, the last else block in the sequence (else/“_”) may rather be documented by functional escape - see above.

##### 7.2.6. Alternative selection block documentation

- Location: above match-block.

- Condition keyword: “Crit”. 
- Condition reason: optionally-quoted Free text. The name of the criterion for alternative selection.

*Example:*

> ````python
>         # [Crit]: visual file suffix
>         match fileName.suffix:
>             # [Alt "familiar file type"]: to open visual file in web browser
>             case '.html' | '.svg' | '.png':
>                 webbrowser.open(f'file://{fileName.resolve().as_posix()}')
>             # [Alt "Unsupported visual format"]: to print reject message
>             case _:
>                 print(f'File type "{fileName.suffix}" not supported yet!')
> 
> ````

##### 7.2.7. Context condition documentation

- Location: above with-block.

-  The condition keyword “Ctxt” in square brackets, followed (within the square brackets) by context-manager part name, the square brackets followed by colon followed by capability name. 

*Example:*

> ````python
>             # [Ctxt "Labeled Fact Renderer Block"]: to restore item dictionary within indented block
>             with self.renderer.LabeledBlock(
>                 self.renderer,
>                 # - Using: to INITIALIZE Raw Fact
>                 RawFact('INFO', quote(label), arg=quote(desc))
>             ):
> ````

- 

##### 7.3. Instance requirement

- Location: Info-bullet under capability-requirement corresponding to a message to an object obtained by a preceding message. Here, Nabu documentation reverses the programmatic call sequence. The required capability corresponds to the last message in the sequence, and the “From” clause underneath corresponds to the initial function call giving the receiver object.
- Format: Info-bullet “From”, followed by capability name.
- Status: automatic. If not specified by the user it will be generated by the Extractor.

*Example:*

> ````python
>     # to perform Unit Test Suite
>     # - From: to INITIALIZE Unit Test Suite Performer
>     unittest.TextTestRunner(
>         verbosity=2
>     ).run(suite)
> ````

###### 7.4. Covariant containment

- Location: Info-bullet under constructor capability-requirement.

- Keyword: “Populates” followed by role-name in square brackets, followed by colon, followed by the populating part. 

  - The role is an association in a super-part (Python superclass) of the current part (Python class).

- (Semantics: indicates that the population of an inherited container is restricted in use cases involving this sub-part. The archetypal example is The “Composite” Pattern, as in the following: “Table Text”, which is kind of “text Composite”, inherits the latter’s “content” container, that accommodates any “Text Component”, and restricts its population to “Table Rows”. While this design decision lacks programmatic significance (the compiler is unaware of it), it has dramatic effect on tracing use cases involving Text Tables).  *Example:*

  > ````python
  >         # to INITIALIZE VG Visual
  >         # - Populates ["fact"]: Use Case
  >         super().__init__(fact, canvas, f'{fact.displayTitle}: {fact.name}')
  > ````

- Status: optional. Not understood automatically by the extractor.

#### 8. Unconditional block documentation
- Location: above and bellow an empty-line-separated section of code. 
- Intent: to compensate for the lack of unconditional block in Python. Less frequently used.

- Consists of a capability name, immediately followed by ellipsis, on the first line, followed by a block of code (that may contain arbitrary Nabu documentation) followed, in the last line, by the same capability name, immediately preceded by ellipsis. 

*Example:*

> ````python
> 
>         # to configure DL/2 restoration...
>         self.version: int = 1
>         self.statSilent: bool = isSilent
>         self.capsDetailed: bool = False
>         self.genAnnotation: bool = cfg.getValue('restore', 'annotation')
>         self.genDefault: bool = cfg.getValue('restore', 'default')
>         # [Opt]: to configure annotation off
>         if not isVerbose:
>             self.genAnnotation = False
>             self.renderer.isVerbose = False
>         # ...to configure DL/2 restoration
> 
> 
> ````

- Status: optional. Not understood automatically by the extractor (that is unaware that an arbitrary sequence of code lines may form a discrete capability).

#### 9. Containment documentation
- Location: above a Nabu part member assignment statement in a constructor method. The member may be either scalar or container. In the latter case, the containment refers to the contained part, rather than the programmatic container type.

- Consists of the keyword “Contains”, followed by “quantity and strength” in square brackets, followed by colon, followed by the target part name (corresponding with the programmatic container-content or scalar member type), optionally followed by role in square brackets. *Example:*

  > ````python
  >             # Contains [1:0-N By Reference] ExternalAgent
  >             self.externals: list[ExternalAgent] = []
  >             # Contains [1:0-1 By Reference] Requirement [Role "active argument"]
  >             self.requirement: Optional[Requirement] = None
  > ````

  - The role, if specified, consists, within square brackets, of the keyword “Role”, followed by the name of the role - optionally-quoted free text, normally inspired by the programmatic container/variable name, word-separated. Unlike containment target that refers to the one (the contained), containment role refers to the many (the container). 
  - Quantity consists of either one or two role-quantities, the latter separated by colon. It is followed by containment strength, which is one of the keywords “By Value” or “By Reference”.. 
    - Role quantity consists of either a natural number or the letter “N” (case insensitive), or two of these (natural number or the letter “N” or asterisk), separated by hyphen. Numbers are normally either “0” or “1”, but other natural numbers are tolerated. 
- There is no need to specify requirement of the constructor capability for 1:1 or 1:0-1 containment of a Nabu-documented part. This is undertood automatically.
- Key specification. Info-bullet consisting of the keyword “Key”, followed by colon, followed by name, which may also be the reserved word “Index”. Corresponds, in dictionaries, to the access key. Also used under lists, (with the keyword “Index”), to emphasize some non-obvious cases of access. *Example:*


> ````python
>      # Contains [1:0-N By Value]: Visual [Role "visual creator"]
>      # - Key: name
>      self.children: dict[int, list[CompositeFactSnippet]] = {}
> ````

- Containment documentation may also feature user–defined info bullets.  *Example:*

> ````python
>         # Contains [1:0-N by Value] Composite Fact Snippet [role "child"] 
>         # - Use: Insert these child snippets when rank falls below this rank. 
>         #        Child snippets ranked zero are inserted at start
>         self.children: dict[int, list[CompositeFactSnippet]] = {}
> ````

- Constructor capability-requirement. *todo…*  *Example:*

  > ````python
  > 
  > ````

- Status: optional. Not understood automatically by the extractor.

#### 10. Unsupported Python features

- Property and property usage.
- The extractor does not infer “magic method” usage. (But will not interfere with you documenting it manually, e.g., over programmatic assignment - it does not look for a function call below).
- *todo…*

#### 11. Recommended best practices

- Conciseness of modifiers.
    - When the subject of a modifier is already apparent from the required capability, omit the detail to avoid unnecessary repetition and keep the code cleaner. 
      - An exception this is when the modifier specifies the *role* (the name of the container) that is scanned, and this selection is not obvious.  
    
    
    *Bad practice:*
    
    > ````python
    > # [Scan "Test modules to run"]: to run the test modules
    > for testModule in test_modules:
    > ````
    
    *Good practice:*
    
    > ````python
    > # [Scan]: to run the test modules
    > for testModule in test_modules:
    > ````

##### 11.1. Capability naming conventions

- In a capability-requirement, where the requiring and required represent a 1:N association, attempt to use verbs that clearly indicate which is on the one side and which is on the many. Typical examples:
  - “to collect” / “to pick”, “to accumulate” / “to add”, “to TRAVERSE” / “to extract”.

*Bad practice:*

> ````python
> # [Opt]: to prepare the redundant list
> if isWithoutDuplicates:
>     # [Scan"; Opt]: to collect duplicates
>     redundant = [x for x in names if isDuplicate(name)]
> ````

*Good practice:*

> ````python
> # [Opt]: to collect duplicates
> if isWithoutDuplicates:
>     # [Scan"; Opt]: to pick duplicate
>     redundant = [x for x in names if isDuplicate(name)]
> ````

- A capability name must reflect intent rather than means, the problem that the capability solves rather than the programmatic machinery that happens to be actually employed to solve it.

*Good practice. Here, We move the main box to the top of the list in order to prioritize its processing over the rest (presuming processing to be conducted in that particular order and on that particular list, which for all we know, is subject to change).*

```python
# [Opt "to get the main Wire Box "]: to prioritize the main box
if (mainBox := self.getMainBox()):
    boxes.remove(mainBox)
    boxes.insert(0, mainBox)
```

*Bad practice. It takes profound knowledge of the problem domain to understand why moving the main box to the top of some list matters!*

```python
# [Opt "to get the main Wire Box "]: to move main box to top of list
if (mainBox := self.getMainBox()):
    boxes.remove(mainBox)
    boxes.insert(0, mainBox)
```



#### 13. The Nabu Extractor and the `nabudoc` Refresher Utility

##### 13.1. Role of the Extractor

The **Nabu Extractor** is the bridge between source code and the Nabu design model. It reads Python (or JavaScript) source files via a tree-sitter AST, identifies documented and undocumented constructs, and emits a **snippet** — a textual representation of the design facts it could infer.

The extractor operates in two modes:

1. **Documented mode** — the developer has placed a Nabu doc-comment (e.g. `# [Opt]: to validate input`) immediately above a control construct. The extractor uses that documentation verbatim.
2. **Synthesis mode** — no doc-comment is present. The extractor synthesizes a best-effort capability name from the surrounding code (variable names, condition expressions, loop targets). When no context is available, it falls back to the **capability numerator**, which produces a unique `to do RENAME ME {stem}-{line} {N:04d}` placeholder. These appear as `RENAME ME` items in the snippet output.

> **Important:** The extractor *never* emits the string `to ...` as a capability name — that is syntactically invalid. Any such string you see in the source was injected by the `nabudoc` tool (see below) as a placeholder awaiting developer input.

##### 13.2. Synthesis Rules by Construct Type

| Construct | Documented (`[X]: to verb obj`) | Undocumented |
|---|---|---|
| `for` loop | Uses doc as-is | Synthesizes `to collect {target}` or `to scan {iterable}` |
| `while` loop | Uses doc as-is | Falls back to numerator |
| `if`/`elif`/`else` | Uses doc per-branch | Falls back to numerator per branch |
| `with` block | `[Ctxt "Part"]: capability` → CONTEXT | Infers CONTEXT from `self.X.method()` pattern; otherwise unconditional |
| list/set/dict comprehension | Uses doc; annotates SCANNING `[COMPACT LIST]` | Synthesizes `to collect {variable}` + compact type |
| Generator expression | Uses doc; annotates `[COMPACT GENERATOR]` | Synthesizes `to collect {variable}` |
| ternary-if (single arm) | Uses outer doc if unconditional | Synthesizes `to decide {target}` |
| ternary-if (chain) | Reads per-arm `[Alt]` docs | Synthesizes `to decide {target}` for whole chain |

##### 13.3. The `nabudoc` Refresher Utility

The `nabudoc` utility (`programs/nabudoc.py`) automates the first pass of Nabu-documentation for an existing source file. It is the **recommended starting point** before hand-authoring any doc-comments.

**Invocation:**
```
python programs/nabudoc.py <source_file.py>
python programs/nabudoc.py <source_file.py> <pre-captured-extractor-output.txt>
```

**What it does — two phases:**

**Phase 1 — RENAME ME injection.**
Runs the extractor on the source file, finds all `RENAME ME` items in the snippet output (i.e. undocumented constructs the extractor could not name), and inserts the appropriate Nabu bracket tag above each construct:
- Determines the condition type from the DOM structure: `[Opt]`, `[Alt "criterion"]`, `[Esc "pre"]`, `[Scan "container"]`, `[Rpt]`, `[Msg]`
- Synthesizes a capability name from the available context (criterion text, iterable variable, PRE condition). When no context is available, uses the **line-number-keyed numerator** to emit `to rename me {N:04d}` — a syntactically valid, unique, clearly-labelled placeholder.

**Phase 2 — Gap scan and improvement.**
Makes a second pass over the source looking for three additional gap types:

| Gap | Action |
|---|---|
| Free-form comment above control construct | Normalises to Nabu format, or marks as `RENAME ME` if normalisation fails |
| Valid `to verb obj` without a bracket tag | Infers and adds the correct bracket tag for the construct |
| Nabu annotation with the wrong bracket tag | Corrects the tag to match the actual construct |

**Policy — synthesized names:**
All capability names injected by `nabudoc` are **valid** Nabu capability names that pass the extractor's `isCapabilityName` check. The string `to rename me {N:04d}` is intentionally chosen: it is valid (starts with `to`), unique (keyed to source line), and self-evidently provisional.

> The developer's task after running `nabudoc` is to search for `rename me` in the source and replace each instance with a meaningful description of the design intent.

**When to run `nabudoc`:**
- When starting documentation on a previously undocumented (e.g. third-party or legacy) source file.
- When adding a large block of new code and needing a quick structural scan.
- After a significant refactor, to catch newly-uncovered branches.

It is **not** necessary to run `nabudoc` on every save — the extractor handles undocumented constructs gracefully through synthesis.

#### 12. Change log

- 31-Dec-2025, Avner Ben.
- 5-Jan-2026, Avner Ben:
  - Added “Capability naming conventions” sub-section to "Recommended best practices", with first item.
- 2-Jan-2026, Avner Ben:
  - Module documentation redefined, introducing the new three-level structure.
- 5-Jan-2026, Antigravity:
  - Added "Recommended best practices" section, advising on the conciseness of modifiers when the context is evident from the capability name.
- 28-Apr-2026, Antigravity (v0.8.36):
  - Added section 2.1 "Selective Extraction — The `[Ignored]` Prefix".
- 28-Apr-2026, Antigravity (v0.8.37):
  - Added section 2.2 "Compact Generation Hint — `[COMPACT]`", covering SCANNING and CRITERION compact modifiers, extractor auto-inference, language-agnostic semantics, and the cognitive dissonance note for hand-authored improvement intent.
  - Documents the new language-agnostic `[Ignored]:` bracket prefix, applicable to Module, Part, Capability, and Requirement facts.
  - Specifies depth-wise suppression semantics, prefix-group priority rule, and case-insensitivity.
