# Extensions Demo

This demo showcases various Markdown extensions supported by Mono.

## Nowrap Extension
You can prevent text from wrapping using the nowrap syntax: {{This text will not wrap even if the container is very small.}}

## Code Block Extension
Code blocks are automatically highlighted and wrapped in the `mono-code-block` component.

```python
def hello_world():
    print("Hello, Mono!")
```

## Colab Extension
Links to `.ipynb` files on GitHub are automatically converted into "Open in Colab" buttons.

[View Notebook Example](https://github.com/example/repo/blob/main/example.ipynb)
