# Notebook Component Demo

The `mono-notebook-input` component is used to create a multi-line notebook-style input area.

## Usage
`@[notebook: <title>, placeholder: <placeholder>](id: <id>)`

## Simple Demos

### Notebook with Title
@[notebook: "Daily Journal", placeholder: "Write your thoughts here..."](id: journal-1)

### Anonymous Notebook
@[notebook: placeholder: "Quick notes..."](id: note-1)

## Advanced Demos

### Notebook in a Row Layout
Two separate notebooks side-by-side.

@[row]
:::column
@[notebook: "Pros", placeholder: "List the pros..."](id: pros-1)
:::
@[spacer: width: 20px]
:::column
@[notebook: "Cons", placeholder: "List the cons..."](id: cons-1)
:::
@[/row]

### Notebook grouped with Poll
Gather input and take notes on the same topic.

@[poll: "Are you enjoying the workshop?", options: "Yes, No, Maybe"]
@[notebook: "Any additional comments?", placeholder: "Write more details..."](id: feedback-1)

## Additional Examples
@[notebook: "My Notes", placeholder: "Start typing..."](id: "note-123")
