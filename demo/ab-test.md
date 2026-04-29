# A/B Test Component Demo

The `mono-ab-test` component is used to present an A/B test between two media sources (images or audio).

## Usage
`@[ab-test: <title>, src-a: <src_a>, src-b: <src_b>]`

## Simple Demos

### Image A/B Test
Compare two SVG files.
@[ab-test: Vector vs XML, src-a: test.svg, src-b: test_xml.svg]

### Remote Image A/B Test
Compare two remote images.
@[ab-test: Image Comparison, src-a: https://picsum.photos/400/300?random=1, src-b: https://picsum.photos/400/300?random=2]

## Advanced Demos

### Combined with Layout and Spacer
Using row layout to display two A/B tests side-by-side with a spacer in between.

@[row]
:::column
@[ab-test: Test 1, src-a: test.svg, src-b: test_xml.svg]
:::
@[spacer: width: 20px]
:::column
@[ab-test: Test 2, src-a: test_xml.svg, src-b: test.svg]
:::
@[/row]
