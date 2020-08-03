# identy

Generate grayscale identity icons.

## Usage

```python
import identy

print(identy.from_string('identy', v=1))
print()
print(identy.random().png().base64str())

# You can save the icon
identy.random().png(256).save('/path/to/file.png')
```

    ████████████████
    ████░░    ░░████
    ██▓▓▓▓▓▓▓▓▓▓▓▓██
    ██▒▒▒▒░░░░▒▒▒▒██
    ██▒▒▒▒░░░░▒▒▒▒██
    ██▓▓▓▓▓▓▓▓▓▓▓▓██
    ████░░    ░░████
    ████████████████

    iVBORw0KGgoAAAANSUh...

> __Note__: The `str` representation of the icon may differ from the generated png image.
