# 🚀 Mono Ultimate Showcase

Welcome! This document is an interactive showcase utilizing all available `Mono` Web Components.

## 1. Landing (Hero & Clock)

@[hero: "Welcome to Mono Showcase"](bg-color: #f8f9fa, text-color: #333)
@[clock](display: block)
Experience the power of Interactive Markdown.
@[/hero]

## 2. Session Management (Session Join & Group Assignment)

@[row]
:::column
@[session-join: "Join Today's Workshop"]
:::
@[spacer](width: 20px)
:::column
@[group-assignment: "Team Allocation"]
:::
@[/row]

## 3. Interactive Inputs (Textfield, Notebook, Poll)

Let's gather some information!

@[row]
:::column
**Quick Question:**
@[textfield: "What is your role?"](size: 30)

**Your Thoughts:**
@[notebook: "Notes"](id: showcase-notebook-1, placeholder: "Type your ideas here...")
:::
@[spacer](width: 20px)
:::column
**Feedback Poll:**
@[poll: "How do you rate the layout?"](options: "Excellent, Good, Needs Improvement")
:::
@[/row]

## 4. Media & Testing (A/B Test, Sound, Score, Reaction)

Listen to the audio, view the music score, and compare designs!

@[row]
:::column
**A/B Image Test:**
@[ab-test: "Design Comparison"](src-a: test.svg, src-b: test_xml.svg)
@[reaction](options: "A is better, B is better")
:::
@[spacer](width: 20px)
:::column
**Audio & Score:**
@[score: "C4 D4 E4 F4 | G4 A4 B4 C5"](clef: treble, time: 4/4)
@[sound: "Play Note"](src: https://actions.google.com/sounds/v1/alarms/beep_short.ogg)
:::
@[/row]

## 5. UI Elements (Drawer, Icon)

@[drawer: Additional Tools](position: right)
Here are some icons you might find useful:
@[row]
:::column
@[icon: "settings"](size: 32px) Settings
:::
:::column
@[icon: "favorite"](size: 32px, color: red) Favorite
:::
@[/row]
@[/drawer]

---
*Created with [Mono]*
