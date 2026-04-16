# Markdown Component Directives

This project supports several custom Markdown components implemented as Web Components. You can inject these components into your Markdown files using custom directives.

Below is the documentation for the available custom directives and their syntax.

## Interactive & Media Components

### A/B Test (`mono-ab-test`)
Used to present an A/B test between two media sources (images or audio).

**Syntax:**
```markdown
@[ab-test: <title>](src-a: <src_a>, src-b: <src_b>)
```
*   `title`: The title of the A/B test.
*   `src_a`: Path or URL to the first media source.
*   `src_b`: Path or URL to the second media source.

Result:
@[ab-test: <title>](src-a: <src_a>, src-b: <src_b>)

---

### Sound (`mono-sound`)
Used to embed a playable sound file.

**Syntax:**
```markdown
@[sound: <label>](src: <src>)
```
*   `label`: (Optional) Text label to display.
*   `src`: Path or URL to the audio file.

Result:
@[sound: <label>](src: <src>)

Alternative syntax without a label:
```markdown
@[sound](src: <src>)
```

---
### Icon (`mono-icon`)
Used to display Google Material Symbols.

**Syntax:**
```markdown
@[icon: <name>](size: <size>, color: <color>, display: <display>)
```
*   `name`: The name of the Material Symbol (e.g., `search`, `home`).
*   The arguments in parentheses are optional:
    *   `size`: CSS size value (e.g., `24px`).
    *   `color`: CSS color value (e.g., `red`, `rgba(255, 0, 0, 0.5)`).
    *   `display`: CSS display value (e.g., `inline-block`).

Result:
@[icon: "home"](size: 64px)

Alternative syntax:
```markdown
@[icon: <name>]
```

---

### Clock (`mono-clock`)
Used to embed a real-time clock.

**Syntax:**
```markdown
@[clock](format: <format>, display: <display>)
```
*   The arguments in parentheses are optional:
    *   `format`: Time format string.
    *   `display`: CSS display value.

Result:
@[clock]

Alternative syntax:
```markdown
@[clock]
```

## Form & Input Components

### TextField Input (`mono-textfield-input`)
Used to create a single-line text input field.

**Syntax:**
```markdown
@[textfield: <placeholder>](size: <size>) or @[textfield](placeholder: <placeholder>, size: <size>)
```
*   `size`: Number indicating the size attribute of the input.
*   `placeholder`: The placeholder text for the input.

Alternative syntax without explicit size:
```markdown
@[textfield: <placeholder>]
```
*(Also supports misspelled directive `@[textfiled: ...]`).*

### Notebook Input (`mono-notebook-input`)
Used to create a multi-line notebook-style input area.

**Syntax:**
```markdown
@[notebook: <title>](id: <id>, placeholder: <placeholder>)
```
*   `title`: (Optional) The title of the notebook input area.
*   `id`: The unique identifier for this input block.
*   `placeholder`: (Optional) The placeholder text to display in the input area.

### Poll (`mono-poll`)
Used to create a polling interface with multiple options.

**Syntax:**
```markdown
@[poll: <title>](options: <options>)
```
*   `title`: The question or title of the poll.
*   `options`: Comma-separated list of poll options.

### Reaction (`mono-reaction`)
Used to embed interactive reaction buttons.

**Syntax:**
```markdown
@[reaction](options: "<options>")
```
*   `options`: Comma-separated list of reaction emojis or texts. Quotes around the options are optional.

## Classroom & Session Components

### Group Assignment (`mono-group-assignment`)
Used to designate group assignments.

**Syntax:**
```markdown
@[group-assignment: "<title>"]
```
*   `title`: Title for the group assignment block. Quotes around the title are optional.

### Session Join (`mono-session-join`)
Used to display a session join component.

**Syntax:**
```markdown
@[session-join: "<title>"]
```
*   `title`: Title for the session join block. Quotes around the title are optional.

## Layout & Formatting Components

### Hero (`mono-hero`)
Used to create a full-screen landing page style hero section.

**Syntax:**
```markdown
@[hero: <title>](image: <image_url>, mode: <mode>, bg-color: <bg_color>, text-color: <text_color>)
...content...
@[/hero]
```
*   `title`: (Optional) The main title to display in the center.
*   `image`: (Optional) Background image URL.
*   `mode`: (Optional) `cover` (default) or `contain`/`fit`.
*   `bg-color`: (Optional) Background color.
*   `text-color`: (Optional) Text color.

### Layout (`mono-layout`)
Used to create flexbox-based layouts such as rows and stacks (columns).

**Row Syntax:**
```markdown
@[row: <classes>]
...content...
@[/row]
```
*   `classes`: (Optional) CSS class names to apply to the row.
*   Alternative: `@[row]`

**Stack Syntax:**
```markdown
@[stack: <classes>]
...content...
@[/stack]
```
*   `classes`: (Optional) CSS class names to apply to the stack.
*   Alternative: `@[stack]`

**Column Layout inside Row/Stack:**
Use the following markers to define columns within a layout block:
```markdown
@[column]
Content for column 1
@[/column]
@[column]
Content for column 2
@[/column]
```

### Spacer (`mono-spacer`)
Used to insert empty space (horizontal or vertical) in the layout.

**Syntax:**
```markdown
@[spacer](width: <width>, height: <height>)
```
*   `width`: CSS width value.
*   `height`: (Optional) CSS height value. If omitted, defaults to the width value.

Alternative syntax:
```markdown
@[spacer](width: <size>)
```

---

*Note: Some components (like `mono-brush`, `mono-code-block`, `mono-export`, and `mono-sync`) are system-level or injected automatically and do not require custom Markdown directives to be manually written in the text.*
