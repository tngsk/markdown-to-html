# Sound Component Demo

The `mono-sound` component is used to embed a playable sound file.

## Usage
`@[sound: <label>](src: <src>)`
or
`@[sound](src: <src>)`

## Simple Demos

### Sound with label
@[sound: Play notification](src: https://actions.google.com/sounds/v1/alarms/beep_short.ogg)

### Sound without label
@[sound](src: https://actions.google.com/sounds/v1/alarms/beep_short.ogg)

## Advanced Demos

### Combined with Layout and Reaction
A grid of sounds with reactions below.

@[row]
:::column
@[sound: Drum Roll](src: https://actions.google.com/sounds/v1/cartoon/drum_roll.ogg)
@[reaction](options: "Wow!, Next")
:::
@[spacer](width: 20px)
:::column
@[sound: Applause](src: https://actions.google.com/sounds/v1/crowds/light_applause.ogg)
@[reaction](options: "👏, 👎")
:::
@[/row]

## Additional Examples
@[sound: "Alert"](src: "https://actions.google.com/sounds/v1/alarms/beep_short.ogg")
