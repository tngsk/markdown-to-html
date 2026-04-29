# Icon Component Demo

The `mono-icon` component is used to display Google Material Symbols.

## Usage
`@[icon: <name>, size: <size>, color: <color>, display: <display>]`
or
`@[icon: <name>]`

## Simple Demos

### Default Icon
@[icon: "home"]

### Icon with Size and Color
@[icon: "search", size: 48px, color: red]

### Icon with RGBA Color
@[icon: "settings", size: 64px, color: rgba(0, 0, 255, 0.5])

## Advanced Demos

### Icon within Hero Component
Using an icon prominently in a Hero component.

@[hero: Welcome!]
@[icon: "star", size: 100px, color: gold]
Enjoy the experience!
@[/hero]

### Icon Grid Layout
Displaying a grid of icons.

@[row]
:::column
@[icon: "thumb_up", size: 32px, color: green]
:::
:::column
@[icon: "thumb_down", size: 32px, color: red]
:::
:::column
@[icon: "favorite", size: 32px, color: pink]
:::
@[/row]

## Additional Examples
@[icon: "star", size: "48px", color: "blue", display: "block"]
