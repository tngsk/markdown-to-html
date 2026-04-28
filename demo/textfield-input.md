# TextField Input Component Demo

The `mono-textfield-input` component is used to create a single-line text input field.

## Usage
`@[textfield: <placeholder>](size: <size>)` or `@[textfield](placeholder: <placeholder>, size: <size>)`

## Simple Demos

### Default Textfield
@[textfield: "Enter your name here"]

### Textfield with explicit size
@[textfield: "Your age"](size: 10)

## Advanced Demos

### Combined with Layout for a Form
Creating a simple form layout.

@[row]
:::column
**First Name:**
@[textfield: "First Name"](size: 20)
:::
@[spacer](width: 20px)
:::column
**Last Name:**
@[textfield: "Last Name"](size: 20)
:::
@[/row]

### Textfield within a Drawer
Hiding the input inside a sliding drawer.

@[drawer: Quick Feedback](position: right)
Please leave a quick note:
@[textfield: "Your feedback..."](size: 30)
@[/drawer]

## Additional Examples
@[textfield-input](placeholder: "Enter details", size: "large")
