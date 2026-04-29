# Clock Component Demo

The `mono-clock` component is used to embed a real-time clock.

## Usage
`@[clock: format: <format>, display: <display>]`
or
`@[clock]`

## Simple Demos

### Default Clock
@[clock]

### Clock with Format
(If format string is supported by your parser)
@[clock: format: "YYYY-MM-DD HH:mm:ss"]

## Advanced Demos

### Clock in a Header/Hero
A clock placed inside a full-screen hero section.

@[hero: Current Time]
@[clock: display: block]
Start your work now!
@[/hero]

### Clock Side-by-Side
Showing multiple clocks in a row.

@[row]
:::column
**Local Time**
@[clock]
:::
@[spacer: width: 50px]
:::column
**Server Time**
@[clock]
:::
@[/row]
