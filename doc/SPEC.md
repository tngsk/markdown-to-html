# Mono Specification

This document defines the core specification for the Mono Markdown to HTML conversion tool, ensuring long-term stability, accessibility, and platform independence.

## 1. Markdown Extension Syntax

Mono extends standard Markdown to support custom interactive components (Web Components) using a consistent, declarative syntax.

### Component Invocation

Components are invoked using the `@[]` syntax.

**Format:**
`@[component-name: optional_label](key: "value", key2: "value2")`

*   `component-name`: The hyphenated name of the Web Component (e.g., `mono-poll`, `mono-flipcard`).
*   `optional_label`: An optional text label passed to the component (often used as a primary text or title).
*   `(key: "value", ...)`: A comma-separated list of key-value pairs providing configuration options. Keys are unquoted, values are string literals enclosed in double quotes. The colon `:` is the standard delimiter.

**Example:**
```markdown
@[mono-poll: Favorite Language?](options: "Python, JavaScript, Rust")
```

### Deprecation Notice
The legacy `=` delimiter (e.g., `key="value"`) is deprecated but supported with a warning during parsing.

## 2. Output HTML Structure & Attributes

To guarantee styling consistency and future-proof the generated HTML, Mono enforces specific structural patterns and data attributes.

### Component Tagging
Each component invocation in Markdown must parse into an explicit HTML tag matching the component name.
*   **Markdown:** `@[mono-flipcard](front: "A", back: "B")`
*   **HTML Output:** `<mono-flipcard front="A" back="B"></mono-flipcard>`

### Required Attributes
*   `data-mono-version`: (Planned) The generated HTML `<body>` or a `<meta>` tag will include the Mono compiler version (e.g., `data-mono-version="1.0.0"`) to support future compatibility layers.
*   The `class` attribute is reserved for utility classes defined in `base.css` (e.g., `.text-large`, layout classes in `mono-layout`).

## 3. Component Behavior (State Machine)

Interactive Mono components follow a predictable state lifecycle, often extending a base `MonoInteractiveElement` for consistent behavior.

1.  **Initialization (`connectedCallback`)**: Component attaches to the DOM, reads initial attributes, and checks `localStorage` for prior state.
2.  **Authentication (`mono-auth-changed`)**: Components listen for global auth events to toggle interactive states (e.g., enabling voting only after login).
3.  **Interaction**: User input updates internal state.
4.  **Storage / Sync**: State changes are saved locally (`localStorage` with `mono_` prefix) and broadcast globally via CustomEvents (e.g., `mono:vote`) for synchronization.

## 4. Accessibility (a11y) Standards

Mono components are designed with accessibility as a first-class requirement.

*   **Role-Based Design**: Components must specify standard ARIA roles (e.g., `role="form"`, `role="button"`).
*   **Keyboard Navigation**: Components must be fully operable via keyboard. Focus management (e.g., focus traps for modals) is handled internally within the Shadow DOM.
*   **Color Independence**: Information must not rely solely on color. Status (success, error) should be conveyed via icons or text, alongside semantic ARIA attributes.
