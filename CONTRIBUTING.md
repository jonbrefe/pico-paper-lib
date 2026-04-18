# Contributing to pico-paper-lib

Thanks for your interest in contributing! This is a small MicroPython library
for e-paper displays, and contributions are welcome.

## How to Contribute

### Reporting Bugs

Open a [GitHub Issue](https://github.com/jonbrefe/pico-paper-lib/issues) with:

- What you expected vs. what happened
- MicroPython version (`import sys; print(sys.version)`)
- Pico board variant (Pico W, Pico 2, etc.)
- Minimal code to reproduce the issue

### Suggesting Features

Open an issue tagged **enhancement**. Describe the use case and how you'd
expect the API to look.

### Submitting Code

1. Fork the repository
2. Create a feature branch (`git checkout -b my-feature`)
3. Make your changes
4. Test on actual hardware (Pico W + 2.9" e-paper) — there is no simulator
5. Ensure all examples still run (`test_all.py`)
6. Submit a pull request

## Code Style

- **Pure MicroPython** — no CPython-only features
- All public functions and classes must have docstrings
- Private helpers (prefix `_`) should have a one-line docstring
- Use `SPDX-License-Identifier: MIT` header on new `.py` files
- Column-major bitmap format: each byte = one column, LSB = top row
- `const()` values cannot be imported across modules — use plain variables for cross-module constants

## Testing

There is no automated test suite. Testing is visual — upload `test_all.py`
to a Pico W and verify all 7 pages render correctly on the e-paper display.

```bash
cd ../pico-ctl
pico_ctl upload ../pico-paper-lib/examples/test_all.py /test_all.py
pico_ctl run test_all.py
```

## License

By contributing, you agree that your contributions will be licensed under the
MIT License.
