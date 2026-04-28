# Reaction Component Demo

The `mono-reaction` component is used to embed interactive reaction buttons.

## Usage
`@[reaction](options: "<options>")`

## Simple Demos

### Emoji Reactions
@[reaction](options: "👍, 👎, 💖, 😢")

### Text Reactions
@[reaction](options: "Awesome, Boring, Needs Work")

## Advanced Demos

### Reactions on A/B Tests
Providing quick feedback on design choices.

@[ab-test: "Which design is better?"](src-a: test.svg, src-b: test_xml.svg)
@[reaction](options: "Design A, Design B, Both are great")

### Reactions under a Hero Section
Ask for immediate sentiment upon viewing a landing page.

@[hero: "Welcome to Mono"]
@[reaction](options: "Let's go!, I'm not sure...")
@[/hero]

## Additional Examples
@[reaction](options: "❤️, 👎, 🚀")
