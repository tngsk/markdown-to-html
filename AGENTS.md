# Developer Guidelines (AGENTS.md)

## AI Agent Directives (Strictly Enforced)
* **Pre-commit Step Formatting:** When creating an execution plan, the pre-commit step description must perfectly match this exact string (including the hyphen): `Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.`
* **Deep Planning Mode:** Before making any code changes, actively use `request_user_input` or `message_user` to ask clarifying questions until you have absolute certainty of expectations. Only create and set a plan (`set_plan`) after receiving these answers. Once the plan is approved, proceed with autonomous execution without further questions.
* **Verification & Specificity in Plans:** Always include an explicit verification step using tools like `read_file` or `cat` after creating/modifying files. Specify concrete tools/commands for every step (e.g., `Use cat to verify parser.py` rather than vague phrases like `Verify modified files`).
* **Test Inclusion:** Always include a step to run tests (e.g., `uv run pytest`) even for pure documentation/reporting tasks. Place it before the pre-commit step.
* **Groundedness Rule:** Never assume code details (like CSS constants or component configuration options) exist based on prior knowledge. Always definitively confirm them by fully inspecting the source files in the trace (e.g., using `grep` or untruncated `cat` outputs) prior to plan creation.
* **Git Operations:** The use of Git force options (e.g., `git add -f`, `git push --force`) is strictly prohibited. Do not forcefully add private files listed in `.gitignore`.
* **Investigation Tasks:** For investigation tasks, strictly adhere to the rule of not implementing or modifying application code until explicit permission is granted by the user. Deliver findings as a report (e.g., a markdown file) and wait for further instructions.
* **Bolt Persona Learnings:** Document critical codebase-specific performance learnings (architectural bottlenecks, surprising failures, or edge cases) in `.jules/bolt.md` using the format:
  ```markdown
  ## YYYY-MM-DD - [Title]
  **Learning:** [Insight]
  **Action:** [How to apply next time]
  ```
* **No Direct Edit of Artifacts:** Never manually edit auto-generated output files (e.g., `output.html`). Always modify the underlying conversion logic, generators, or templates. Do not commit these generated test artifacts.

## Architecture & Code Structure
* **Source of Truth:** `doc/ARCHITECTURE.md` serves as the authoritative, immutable source of truth for architectural decisions and project state. It must not be altered when updating other documentation like `doc/NOTES.md`.
* **Single Output HTML:** The Mono project enforces a single, self-contained, offline-capable HTML output relying on a pure Python toolchain (`uv`).
* **Global CSS Frameworks Prohibited:** Adopting global utility CSS frameworks (like Tailwind/DaisyUI) introduces severe architectural conflicts (requires Node.js build dependencies, breaks encapsulation with Shadow DOM, causes massive file bloat for offline capability). Do not use them.
* **Separation of Concerns:** Hardcoding HTML, CSS, and JS is strictly prohibited. Keep setups minimal and use separate CSS/JS files or classes instead of inline styles or scripts in Python or HTML templates.
* **Dependency Management:** Use `uv` for dependency management. Set up the development environment with `uv sync`.
* **Configuration:** Avoid YAML Frontmatter. Use `config.toml` for managing configuration settings.
* **Error Handling:** All scripts must include robust error handling and exit safely on signals like `SIGINT`.
* **Python String Optimization:** When optimizing character-by-character string parsing loops in Python, character-by-character list appending and `"".join()` is a bottleneck. Implement a fast path using `str.split(',')` for simple cases without nested quotes/parentheses, and use index-based string slicing (`string[start_idx:i]`) for the fallback parser.

## Markdown & Converter Specifications
* **Markdown Converter Execution:** `uv run main.py <input.md> -o <output.html>`
* **Markdown Extensions:** Python-Markdown extensions (e.g., `attr_list`) are configured and enabled by adding their module names to the `MARKDOWN_EXTENSIONS` list in `src/constants.py`.
* **Text Sizing in Markdown:** For simple text size variations in Markdown without custom components, use utility classes `.text-small` (0.5rem), `.text-large` (1.5rem), and `.text-xlarge` (3rem) defined in `src/templates/core/base.css` with the `attr_list` extension (e.g., `[text]{.text-large}`).
* **Custom Markdown Syntax:** Design proprietary Markdown extension syntax with future integration for external sensor data in mind.
* **File Size Limit:** A strict maximum limit of 30MB for HTML file sizes is enforced during build validation (bypassable with the `--force` CLI flag). A warning is issued if the size exceeds 20MB, logging the size contribution of embedded assets.
* **Asset Optimization:** 'Mono' uses an Asynchronous Injection Strategy, lazy-loading Base64 assets from a hidden JSON template store, converting images to WebP with Pillow, and inlining SVG XML directly for performance.
* **DOM Manipulation:** Use Python's standard `re` (regex) for DOM manipulation to achieve fast and memory-efficient stream-like replacement.
* **PDF Export:** To output Mono pages as single, monolithic PDFs without page breaks, use Playwright (`sync_api`) and set the `page.pdf()` dimensions dynamically to match the document's `scrollWidth` and `scrollHeight`. When importing Playwright, place the import statement locally inside the execution method and catch `ImportError` to gracefully degrade.

## Web Components & Frontend
* **Implementation:** Web Components are implemented using Vanilla JS without external dependencies, utilizing a "Template Injection Strategy". Component files must be structured as `template.html` and `script.js` inside their `components/<component-name>/` directory.
* **Component Invocation:** Custom Web Components are typically invoked in Markdown using the syntax `@[component-name: label](key: "value", key2: "value2")`.
* **Parameter Parsing:** The `BaseComponentParser.parse_key_value_args` function designates `:` as the standard delimiter for key-value pairs (e.g., `key: "value"`). The `=` delimiter is deprecated but temporarily supported via fallback parsing that emits a deprecation warning.
* **Explicit Output Tags:** Component parsers (like `parser.py`) must output the explicit `<mono-component-name>` tag verbatim. If they don't, `processors/html.py` (which searches for `r'<(mono-[a-z0-9-]+)'`) will not automatically inject the component's assets into the final HTML output.
* **Component Injection Logic:** Component templates and scripts are selectively injected into the output HTML by `processors/html.py`. Exceptions unconditionally included are `<mono-sync>`, `<mono-brush>`, and the `mono-interactive-element.js` base class.
* **Avoid Inline Scripts:** To avoid inline `<script>` tags that set global `window` variables, pass backend configuration values to the frontend using `<meta>` tags (e.g., `<meta name="mono-api-url" content="...">`). Component scripts should read these using `document.querySelector('meta[...]').content`.
* **Data Storage:** Interactive components (like `<mono-poll>`, `<mono-ab-test>`, `<mono-notebook-input>`) save user data in `localStorage` using keys prefixed with `mono_`.
* **Event-Driven Authentication:** The `<mono-account>` component manages the `mono_auth` key in `localStorage` and broadcasts the `mono-auth-changed` event on the `window` object. Subscribers (like `MonoInteractiveElement`) use this to manage user state transitions.
* **MonoInteractiveElement Base Class:** Interactive Vanilla JS components should extend `MonoInteractiveElement` (`src/templates/core/mono-interactive-element.js`). It abstracts boilerplate for race-condition mitigation, `localStorage` (`mono_auth`) checks, and listening for global `mono-auth-changed` events, exposing an `onAuthStateChanged(user)` hook.
* **Cross-Component Communication:** Rely on an event-driven architecture using CustomEvents that bubble up to and are listened for on the global `document` object (e.g., `document.addEventListener('mono:vote', ...)`).
* **Graceful Degradation:** Components should implement graceful degradation using `try...catch` blocks during initialization (e.g., accessing `localStorage`, WebSockets). This ensures fallback to a standalone mode without causing a page-level crash if a dependency fails.
* **Data Passing (Python to HTML):** When dynamically passing JSON data from Python to HTML components via `<script type="application/json">`, safely escape it using `json.dumps(data).replace('<', '\u003c').replace('>', '\u003e').replace('&', '\u0026')` to prevent XSS.
* **Visualizations:** To avoid large 3rd-party libraries (like Mermaid.js), use hybrid approaches: compute layout data (e.g., DAG layers) in Python to generate HTML/CSS, then use Vanilla JS and SVG strictly for drawing dynamic connectors and annotations.
* **Deprecated Components:** Implicit components (e.g., `mono-code-block`, `mono-brush`, `mono-sync`, `mono-export`) are scheduled for deprecation in the Mono project. Note: `mono-code-block` utilizes a 'Light DOM' enhancement strategy, slotting the original Markdown `<pre><code>` output rather than replacing it. Markdown fenced code blocks (`<pre><code>`) are automatically intercepted and converted into `<mono-code-block>` tags by the `CodeBlockExtension` in `src/extensions/code_block.py`.
* **Frontend Error Handling:** For frontend error handling, use contextual, friendly Japanese messages (e.g., `console.info` with explanations or user-facing `alert`) to guide users, rather than relying solely on raw stack traces or standard `console.error` logs.

## CSS, Theming & Layout
* **Centralized CSS Loading:** CSS loading and injection are fully centralized in `CSSEmbedder` (`src/embedders/css.py`). `HTMLDocumentBuilder` strictly handles HTML structural assembly, while `CSSEmbedder.embed_css_in_html()` handles replacing `{CSS_BLOCK}` placeholders, resolving `themes.toml`, and inserting styles.
* **Theme System:** The project uses a DaisyUI-inspired CSS variable theme system defined in `src/templates/core/themes.toml` (parsed via `tomllib`). Global themes are dynamically applied by modifying the `data-theme` attribute on `<html>`. Users can override the theme using `@[theme: name](config="custom.toml")`.
* **Global Layout & Grid:** The main layout relies on CSS Grid on the `body` element in `src/templates/core/base.css`. Standard content defaults to the center track (`grid-column: var(--component-grid-column, 2)`). Full-bleed web components override this by defining `--component-grid-column: 1 / -1;` in their `:host` Shadow DOM styles. Avoid legacy hacks like negative margins for full-bleed layouts.
* **Grid Overflow Issue:** In `src/templates/core/base.css`, the CSS Grid defines `grid-template-columns: minmax(1rem, 1fr) minmax(auto, 800px) minmax(1rem, 1fr);`. The `auto` value can cause horizontal overflow on smaller screens if content scales up.
* **Image Sizing:** In `src/templates/core/base.css`, the global `img` style must use `max-width: 100%; height: auto;` rather than `width: 100%;` to ensure explicitly sized Markdown images (via the `attr_list` extension, e.g., `{width="100"}`) are respected.
* **Z-Index Variables:** Global z-index levels are centralized in `src/templates/core/base.css` using CSS variables (e.g., `--z-index-overlay`). Web components must reference these variables instead of hardcoding high values.
* **Light DOM Styling:** `::slotted()` can only style top-level direct children. To style deeply nested light DOM elements injected into the component, inject styles globally (e.g., dynamically creating a `<style>` tag in the document head/body from the component's script).
* **Overriding Global Styles in Shadow DOM:** To apply custom text colors to slotted light DOM elements and override global styles (like `base.css`), redefine the global CSS variables (e.g., `--font-color`) on the `:host` selector inside the component's `style.css`. Avoid `::slotted(*)` with `color: inherit` due to high specificity issues.
* **Dynamic Attribute Styling:** To conditionally style Web Components based on attributes parsed from Markdown (e.g., `width="fit"`), leverage CSS attribute selectors like `:host([attribute="value"])` within `style.css`. For dynamic parameters (like background colors), component scripts should map attributes to CSS custom properties on the `:host` element using `this.style.setProperty('--var-name', value)`.
* **Print/PDF CSS:** To ensure interactive Web Components degrade gracefully during static PDF export or printing, apply `@media print` CSS rules in the component's `style.css` to hide interactive parts (`display: none`) and render static alternative text or layout fallbacks. Because `print-color-adjust` is not inherited through the Shadow DOM, components relying on background colors must explicitly include `-webkit-print-color-adjust: exact !important; print-color-adjust: exact !important;` in their `@media print` CSS.
* **Mono-Layout Spacing:** In the `mono-layout` component, horizontal (`@[row]`) and vertical (`@[stack]`) spacing and alignment are natively controlled by passing specific CSS classes as attributes (e.g., `@[row](class: "gap-md center")`).

## Backend & Security (FastAPI)
* **Backend Responsibilities:** `src/server.py` handles real-time visual synchronization via WebSockets (`/ws/sync`) and stores user input data sent via HTTP POST (`/api/data`) in JSONL format. Start with `uv run server.py`.
* **Async I/O Safety:** To avoid race conditions and corrupted data when handling concurrent file writes in async endpoints, use an `asyncio.Queue` and a background worker task to serialize the I/O operations instead of writing directly with `aiofiles.open(..., "a")` in the request handler.
* **Queue Instantiation:** Instantiating `asyncio.Queue()` at the global module level outside of a running event loop will raise a `RuntimeError` in Python 3.10+. Queues should be instantiated safely within an async context, such as a FastAPI `lifespan` event.
* **Security Config:** Use a centralized function like `get_security_config()` in `src/server.py` to load security settings from `config.toml`.
* **Denial of Service (DoS) Prevention:** The `/api/data` endpoint should enforce a maximum payload size limit (default 1MB) configured as `max-upload-size` in the `[security]` section of `config.toml` to prevent DoS attacks via memory exhaustion. Validate both the `Content-Length` header and the actual streaming body size.
* **CSP Headers:** The application reads `config.toml` for security settings, extracting `connect-src` and `ws-src` from the `[security]` section to populate the Content-Security-Policy (CSP) meta tag. Ensure any new external CDN or resources introduced to the frontend are explicitly permitted in the dynamically generated CSP meta tag in `processors/html.py`.
* **Path Traversal Security:** When writing path traversal security checks (e.g., in `src/embedders/media.py`), ensure media paths are relative to pre-resolved `markdown_dir` or `Path.cwd()`. Use `pathlib.Path.resolve()` for canonicalization, handle `ValueError` for cross-drive comparisons, and strictly utilize `.is_file()` to prevent directory processing.
* **Component Loading Security:** The Mono project restricts dynamic component loading by maintaining an explicit allowlist named `ALLOWED_COMPONENTS` in `src/constants.py`, ensuring only trusted component directories are imported. Do not use dynamic file system traversal (`iterdir`) and `exec_module` to load components. Instead, dynamically construct the module string and use `importlib.import_module()`.
* **Media Caching Context:** In `src/embedders/media.py`, `MediaEmbedder`'s `_base64_cache` uses a composite key of the file path and `st_mtime` to ensure proper invalidation. If the embedding log reports '0 items' but media is rendered, it is usually because the source `src` already starts with `http://`, `https://`, or `data:`.

## Testing
* **Test Execution:** Use `uv run pytest` to execute tests.
* **Resolving Module Errors:** If you encounter a `ModuleNotFoundError` or `ImportError` (e.g., `No module named 'src'`) when running scripts or tests, prefix the command with `PYTHONPATH=$(pwd)` (e.g., `PYTHONPATH=$(pwd) uv run src/main.py <file>`) to ensure the local source directory is resolvable.
* **Testing Component Parsers:** To unit test component `parser.py` files located in hyphenated directory names (e.g., `src/components/mono-badge/`), use `importlib.util.spec_from_file_location` to dynamically load the module in the test file, as standard Python imports cannot natively resolve paths containing hyphens.
* **Testing FastAPI Lifespan:** When testing FastAPI applications that utilize the `lifespan` context manager, `TestClient` must be used as a context manager (e.g., `with TestClient(app) as client:`) within synchronous tests to trigger startup and shutdown events correctly.

## Documentation Writing
* **User Documentation:** When creating or updating user-facing documentation (e.g., `README.md`), keep it concise and focused purely on usage instructions. Do not include internal development policies or guidelines.

## Security & Defense
* **DOM XSS Prevention:** When extracting JSON data from DOM elements (like `<template>` tags), strictly use `textContent` instead of `innerHTML` to prevent HTML entity decoding and DOM XSS vulnerabilities.
* **URL Validation:** When assigning URLs to `src` attributes in JavaScript components, validate them securely using the `URL` constructor (`new URL(url, window.location.href)`) and explicitly allowlist safe protocols (e.g., `http:`, `https:`, `data:`) to prevent URI injection attacks like `javascript:`.
