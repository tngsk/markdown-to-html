# Layout Component Demo

The `mono-layout` component is used to create flexbox-based layouts such as rows and stacks (columns).

## Usage
**Row Syntax:**
```markdown
@[row: <classes>]
...content...
@[/row]
```

**Stack Syntax:**
```markdown
@[stack: <classes>]
...content...
@[/stack]
```

**Column Layout:**
```markdown
:::column
...
:::
```

## Simple Demos

### Two-Column Row
@[row]
:::column
**Column 1**
Content for the first column.
:::
:::column
**Column 2**
Content for the second column.
:::
@[/row]

### Stack Layout
@[stack]
:::column
**Top Section**
Content at the top.
:::
:::column
**Bottom Section**
Content at the bottom.
:::
@[/stack]

## Advanced Demos

### Complex Dashboard Layout
Combining rows, stacks, and components.

@[row]
:::column
@[stack]
:::column
**Current Time**
@[clock]
:::
:::column
**Quick Actions**
@[icon: "home"] @[icon: "settings"]
:::
@[/stack]
:::
@[spacer](width: 20px)
:::column
**Feedback**
@[poll: "How's the layout?"](options: "Great, Needs Work")
:::
@[/row]

### Media Gallery
Using a row to display multiple interactive media components side by side.

@[row]
:::column
@[ab-test: "Design A vs B"](src-a: test.svg, src-b: test_xml.svg)
:::
@[spacer](width: 10px)
:::column
@[ab-test: "Design C vs D"](src-a: test.svg, src-b: test_xml.svg)
:::
@[/row]
