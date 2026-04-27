# Poll Component Demo

The `mono-poll` component is used to create a polling interface with multiple options.

## Usage
`@[poll: <title>](options: <options>)`

## Simple Demos

### Yes/No Poll
@[poll: "Do you like Markdown?"](options: "Yes, No")

### Multiple Choice Poll
@[poll: "What is your favorite programming language?"](options: "Python, JavaScript, Rust, Go")

## Advanced Demos

### Multiple Polls with Layout
Side-by-side polling questions.

@[row]
:::column
@[poll: "Morning Person?"](options: "Yes, No")
:::
@[spacer](width: 30px)
:::column
@[poll: "Coffee or Tea?"](options: "Coffee, Tea, Neither")
:::
@[/row]

### Poll inside a Drawer
A hidden feedback poll that users can open.

@[drawer: Give Feedback](position: bottom)
Please let us know how we did today!
@[poll: "Rate today's session"](options: "Excellent, Good, Fair, Poor")
@[/drawer]

## Additional Examples
@[poll: "Favorite Color?"](options: "Red, Blue, Green, Yellow")
