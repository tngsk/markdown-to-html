# Hero Component Demo

The `mono-hero` component is used to create a full-screen landing page style hero section.

## Usage
```markdown
@[hero: <title>](image: <image_url>, mode: <mode>, bg-color: <bg_color>, text-color: <text_color>)
...content...
@[/hero]
```

## Simple Demos

### Basic Hero
@[hero: Welcome to Mono]
This is a simple hero section.
@[/hero]

### Hero with Background Color
@[hero: Colored Hero](bg-color: #f0f8ff, text-color: #333)
Enjoy the calm colors!
@[/hero]

## Advanced Demos

### Hero with Background Image and Components
A hero section showcasing an image and a session join button.

@[hero: Join the Adventure](image: https://picsum.photos/1200/800?random=1, text-color: white)
@[session-join: "Start Now"]
@[/hero]

### Nested Layouts within Hero
Using row layouts inside a hero section.

@[hero: Dashboard]
@[row]
:::column
@[clock]
:::
:::column
@[icon: "dashboard"](size: 64px)
:::
@[/row]
@[/hero]
