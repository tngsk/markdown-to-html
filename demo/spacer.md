# Spacer Component Demo

The `mono-spacer` component is used to insert empty space (horizontal or vertical) in the layout.

## Usage
`@[spacer: width: <width>, height: <height>]`
or
`@[spacer: width: <size>]`

## Simple Demos

### Horizontal Spacer
Content A @[spacer: width: 50px] Content B

### Vertical Spacer (using height implicitly)
Content Above
@[spacer: width: 100px]
Content Below

## Advanced Demos

### Formatting a Form Layout
Using spacers to align inputs nicely within a row.

@[row]
:::column
**Name:**
@[spacer: width: 10px]
@[textfield: "Enter Name"]
:::
@[spacer: width: 40px]
:::column
**Email:**
@[spacer: width: 10px]
@[textfield: "Enter Email"]
:::
@[/row]

### Spacing around a Hero Element
Adding breathing room around a major component.

@[spacer: width: 50px]
@[hero: Centered Content, bg-color: #eee]
This hero is padded by spacers!
@[/hero]
@[spacer: width: 50px]

## Additional Examples
Content A @[spacer: width: "50px", height: "20px"] Content B
