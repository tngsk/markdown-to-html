# Group Assignment Component Demo

The `mono-group-assignment` component is used to designate group assignments.

## Usage
`@[group-assignment: "<title>"]`

## Simple Demos

### Default Group Assignment
@[group-assignment: "Team Building Exercise"]

### Anonymous Group Assignment
@[group-assignment]

## Advanced Demos

### Combined with Session Join
Use session join to get everyone in, then assign groups.

@[session-join: "Join the Team Activity"]
---
@[group-assignment: "Now, let's break into groups!"]

### Group Assignment inside a Drawer
Keep the interface clean by hiding group assignments until needed.

@[drawer: Show Group Assigments, position: right]
@[group-assignment: "Workshop Groups"]
@[/drawer]
