# Score Component Demo

The `mono-score` component is used to render a musical score.

## Usage
`@[score: <notes>](clef: <clef>, time: <time>)`

## Simple Demos

### Simple Notes
@[score: "C4 D4 E4 F4 | G4 A4 B4 C5"]

### Score with Clef and Time Signature
@[score: "C4 D4 E4 F4 | G4 A4 B4 C5"](clef: treble, time: 4/4)

## Advanced Demos

### Combining Score and Sound
Display a score alongside an audio playback button.

@[row]
:::column
**Sheet Music**
@[score: "G4 G4 D5 D5 | E5 E5 D5 2 | C5 C5 B4 B4 | A4 A4 G4 2"](clef: treble, time: 4/4)
:::
@[spacer](width: 30px)
:::column
**Play Melody**
@[sound: "Play Melody"](src: https://actions.google.com/sounds/v1/alarms/beep_short.ogg)
:::
@[/row]

### Score within a Drawer
A hidden musical reference drawer.

@[drawer: Musical Reference](position: right)
**C Major Scale**
@[score: "C4 D4 E4 F4 G4 A4 B4 C5"](clef: treble)
@[/drawer]
