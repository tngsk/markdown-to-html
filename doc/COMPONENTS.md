# Markdown Component Directives

This project supports several custom Markdown components implemented as Web Components. You can inject these components into your Markdown files using custom directives.

Below is the documentation for the available custom directives and their syntax.

## Interactive & Media Components

### A/B Test (`situ-ab-test`)
Used to present an A/B test between two media sources (images or audio).

**Syntax:**
```markdown
@[ab-test: <title>](<src_a>, <src_b>)
```
*   `title`: The title of the A/B test.
*   `src_a`: Path or URL to the first media source.
*   `src_b`: Path or URL to the second media source.

### Sound (`situ-sound`)
Used to embed a playable sound file.

**Syntax:**
```markdown
@[sound: <label>](<src>)
```
*   `label`: (Optional) Text label to display.
*   `src`: Path or URL to the audio file.

Alternative syntax without a label:
```markdown
@[sound](<src>)
```

### Icon (`situ-icon`)
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

Alternative syntax:
```markdown
@[icon: <name>]
```

### Clock (`situ-clock`)
Used to embed a real-time clock.

**Syntax:**
```markdown
@[clock](format: <format>, display: <display>)
```
*   The arguments in parentheses are optional:
    *   `format`: Time format string.
    *   `display`: CSS display value.

Alternative syntax:
```markdown
@[clock]
```

## Form & Input Components

### TextField Input (`situ-textfield-input`)
Used to create a single-line text input field.

**Syntax:**
```markdown
@[textfield: size: <size> (<placeholder>)]
```
*   `size`: Number indicating the size attribute of the input.
*   `placeholder`: The placeholder text for the input.

Alternative syntax without explicit size:
```markdown
@[textfield: <placeholder>]
```
*(Also supports misspelled directive `@[textfiled: ...]`).*

### Notebook Input (`situ-notebook-input`)
Used to create a multi-line notebook-style input area.

**Syntax:**
```markdown
@[notebook-input](<id>)
```
*   `id`: The unique identifier for this input block.

### Poll (`situ-poll`)
Used to create a polling interface with multiple options.

**Syntax:**
```markdown
@[poll: <title>](<options>)
```
*   `title`: The question or title of the poll.
*   `options`: Comma-separated list of poll options.

### Reaction (`situ-reaction`)
Used to embed interactive reaction buttons.

**Syntax:**
```markdown
@[reaction: "<options>"]
```
*   `options`: Comma-separated list of reaction emojis or texts. Quotes around the options are optional.

## Classroom & Session Components

### Group Assignment (`situ-group-assignment`)
Used to designate group assignments.

**Syntax:**
```markdown
@[group-assignment: "<title>"]
```
*   `title`: Title for the group assignment block. Quotes around the title are optional.

### Session Join (`situ-session-join`)
Used to display a session join component.

**Syntax:**
```markdown
@[session-join: "<title>"]
```
*   `title`: Title for the session join block. Quotes around the title are optional.

## Layout & Formatting Components

### Layout (`situ-layout`)
Used to create flexbox-based layouts such as rows and stacks (columns).

**Row Syntax:**
```markdown
@[row: <classes>]
...content...
@[end]
```
*   `classes`: (Optional) CSS class names to apply to the row.
*   Alternative: `@[row]`

**Stack Syntax:**
```markdown
@[stack: <classes>]
...content...
@[end]
```
*   `classes`: (Optional) CSS class names to apply to the stack.
*   Alternative: `@[stack]`

**Column Layout inside Row/Stack:**
Use the following markers to define columns within a layout block:
```markdown
:::column
Content for column 1
:::
:::column
Content for column 2
:::
```

### Spacer (`situ-spacer`)
Used to insert empty space (horizontal or vertical) in the layout.

**Syntax:**
```markdown
@[spacer](<width>, <height>)
```
*   `width`: CSS width value.
*   `height`: (Optional) CSS height value. If omitted, defaults to the width value.

Alternative syntax:
```markdown
@[spacer](<size>)
```

---

*Note: Some components (like `situ-brush`, `situ-code-block`, `situ-export`, and `situ-sync`) are system-level or injected automatically and do not require custom Markdown directives to be manually written in the text.*
