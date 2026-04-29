# Session Join Component Demo

The `mono-session-join` component is used to display a session join component.

## Usage
`@[session-join: "<title>"]`

## Simple Demos

### Session Join with Title
@[session-join: "Join the Morning Standup"]

### Anonymous Session Join
@[session-join]

## Advanced Demos

### Session Join in a Hero Section
Make joining the session the main call to action.

@[hero: Welcome to the Class!]
@[session-join: "Click below to join"]
@[/hero]

### Session Join with an initial Poll
Ask a question immediately after joining.

@[session-join: "Join Feedback Session"]
@[poll: "How are you feeling today?", options: "Great, Good, Okay, Bad"]

## Additional Examples
@[session-join: "Join Event"]
