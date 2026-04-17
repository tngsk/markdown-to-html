# Notebook Component Demo

The `mono-notebook-input` component is used to create a multi-line notebook-style input area.

## Usage
`@[notebook: <title>](id: <id>, placeholder: <placeholder>)`

## Simple Demos

### Notebook with Title
@[notebook: "Daily Journal"](id: journal-1, placeholder: "Write your thoughts here...")

### Anonymous Notebook
@[notebook](id: note-1, placeholder: "Quick notes...")

## Advanced Demos

### Notebook in a Row Layout
Two separate notebooks side-by-side.

@[row]
:::column
@[notebook: "Pros"](id: pros-1, placeholder: "List the pros...")
:::
@[spacer](width: 20px)
:::column
@[notebook: "Cons"](id: cons-1, placeholder: "List the cons...")
:::
@[/row]

### Notebook grouped with Poll
Gather input and take notes on the same topic.

@[poll: "Are you enjoying the workshop?"](options: "Yes, No, Maybe")
@[notebook: "Any additional comments?"](id: feedback-1, placeholder: "Write more details...")
