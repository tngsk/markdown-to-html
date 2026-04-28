## 2024-05-18 - HTML String Processing Optimizations
**Learning:** In Python, sequential `in` checks on a large string (e.g., checking if 20 different component tags are in a 1MB HTML body) and multiple sequential `re.sub` calls (e.g., removing multiple excluded tags) can be surprisingly slow, leading to bottlenecks in document building. Custom dictionary replacements for HTML escaping are also much slower than the C-optimized standard library equivalent.
**Action:** Use a single `set(re.findall(...))` pass to extract all present component tags and check against the set. Combine multiple tag-removal regexes into a single pattern using alternation (`|`) and backreferences (`\1`) for opening/closing tags. Always prefer the built-in `html.escape` (followed by a `.replace` if specific entity matching is required) over manual `replace` chaining for performance.

## 2026-04-22 - Optimizing Tokenizer Loops
**Learning:** Writing a character-by-character tokenizer loop in Python to parse component arguments (like `key: "value", key2: func()`) can be a bottleneck compared to regex engines. However, regex engines often fail or become overly complex when parsing nested state structures (like nested parentheses in `calc(var(...))`). While keeping a manual Python string parser loop to track nested state, you can regain performance by avoiding unnecessary list allocations (e.g. use `current.clear()` instead of `current = []`) and using string indexing/built-in `.find(':')` instead of multi-step `.split(':')` inside loops.
**Action:** When you must use a Python character-tracking loop to process stateful tokens (like nested parenthesis), aggressively optimize inside the loop to avoid allocations. Reuse list buffers and prefer `.find()` and slice extraction over generating unneeded intermediate split arrays.

## 2024-05-18 - Optimizing String Iteration Parsing
**Learning:** When optimizing character-by-character string parsing loops in Python (especially for complex structures like nested parentheses where regular expressions fall short or introduce bugs), character-by-character list appending and `"".join()` (even with `.clear()`) is a bottleneck due to excessive object allocations.
**Action:** Implement a fast path using `str.split(',')` for simple cases without nested quotes/parentheses. For the fallback parser, use index-based string slicing (`string[start_idx:i]`) instead of list appending to significantly improve performance.

## 2024-05-24 - Sync I/O in Async Route
**Learning:** Calling synchronous blocking I/O (like reading and parsing a config file) inside an async FastAPI route (like `/api/data`) causes severe performance bottlenecks, blocking the entire event loop.
**Action:** Use `functools.lru_cache` for configuration loading to cache the parsed data so subsequent requests don't hit the disk and parse the file again.
## 2026-04-26 - Image Duplication Optimization
**Learning:** During the media embedding process, repeatedly converting the same image file to Base64 (or reading the same SVG) resulted in unnecessary I/O overhead and significantly bloated the final HTML document's `<template id="mono-asset-store">`.
**Action:** Always maintain a local cache mapping the resolved file path to its generated asset identifier (or SVG content) during the document build process. Check this cache before reading or encoding the file to ensure identical assets are deduplicated in the output.

## 2024-05-24 - Optimizing Parameter Parsing
**Learning:** Python character-by-character loops are extremely slow for parameter parsing (e.g. `BaseComponentParser.parse_bracket_content`).
**Action:** When parsing parameters, check for the absence of complex nesting characters (like `(`, `"`, or `'`) and delegate to C-backed native string methods like `.split(',')` for a massive speedup on simple cases.
