# Drawer Component Demo

The `mono-drawer` component is used to create a sliding drawer tab on the edges of the screen.

## Usage
```markdown
@[drawer: <label>, position: <position>, open: <open>]
...content...
@[/drawer]
```

## Simple Demos

### Left Drawer
@[drawer: Menu, position: left]
* Home
* About
* Contact
@[/drawer]

### Right Drawer
@[drawer: Information, position: right]
This is some extra information on the right.
@[/drawer]

## Advanced Demos

### Drawer with Form Elements
A feedback drawer at the bottom of the screen.

@[drawer: Feedback, position: bottom]
**Please leave your feedback:**
@[textfield: "Comments...", size: 40]
@[reaction: options: "Good, Bad"]
@[/drawer]

### Multiple Drawers
Having drawers on different sides.

@[drawer: Tools, position: left]
@[icon: "build"]
@[icon: "settings"]
@[/drawer]

@[drawer: Notes, position: right]
@[notebook: "Quick Notes", placeholder: "Jot things down..."](id: drawer-note-1)
@[/drawer]

## Additional Examples
@[drawer: "Always Open", position: "right", open: "true"]
Always open drawer
@[end]
