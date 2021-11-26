# negargparse

![Tests](https://github.com/k-sriram/negargparse/actions/workflows/tests.yml/badge.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An ArgumentParser which understands negative numbers.

---

## Getting `negargparse`

The preferred way to use `negargparse` is to copy the module `negargparse.py` into your project. This is because currently one can expect frequent API changes. We do use [semantic versioning](https://semver.org) to help you guard against it.

`negargparse` can also  be installed from PyPI:
```sh
pip install negargparse
```

## Usage

The `argparse` module in python provides tools to parse command line arguments. However, sometimes it doesn't interpret arguments correctly when dealing with negative numbers. Currently `argparse` correctly interprets negative numbers if they are strictly numbers and there are no numeral options like `-1`. However it doesn't work when working with non standard numeral formats. e.g. declination is usually written in the `(+|-)(degree):(arcminute):(arcsecond)` format like `-16:32:45.46`. `argparse` would interpret this as an option, rather than an argument and quit (because of finding an unknown argument) before we have a chance to examine it. Any way to solve this issue requires doing some hacky gymnastics, `negargparse` is here to do that for you.

`negargparse` provides a subclass of `ArgumentParser` called `NegativeArgumentParser`, which escapes all arguments which begin with a '-' followed by a digit. Now declare the type of arguments that you expect to be negative as one of the provided types `NegString`, `NegInt`, `NegFloat` to unescape them.

```python
>>> parser = negargparse.NegativeArgumentParser()
>>> parser.add_argument("eggs", type=NegString)
>>> parser.parse_args(["-23h15m04s"])
Namespace(eggs='-23h15m04s')
```

## [License](./LICENSE)

This repository is distributed under the MIT License, though the module is available under the more permissive MIT-0 license. See the [LICENSE](./LICENSE) or at the top of the [module](negargparse/negargparse.py) for the license text.

## Known issues

Right now this project is more or less a framework to develop the module. Except for some narrow cases, it breaks more pre-existing functionality of `argparse` than provide new ones. Right now you are better off not using this if that bothers you.

- If the user types a negative number in an unexpected (not of the provided NegString etc. types) argument, this would escape the said field, but since it is not declared as a NegString/NegInt/NegFloat, it wouldn't be unescaped.

- This module doesn't respect the POSIX convention of leaving the arguments after `--`.

- Currently single digit options are unusable.

- This project currently lacks support for versions earlier than python 3.7. This is not because of lack of any features in python 3.6, but because of lack of support for annotations used in this module. At the release of v1, a special untyped release for python 3.6 shall be made.

## Development

This section tells you how to set up the development environment and run tests, which can be used to either modify the module for their own purpose of for potential contributors.

### Setup development environment

Ensure `python` >= 3.8

Ensure you have `poetry` installed. You can get it from https://github.com/python-poetry/poetry. This requires `poetry`  >=1.2 which is currently only released as alpha.

1. Clone the repository
2. Install the package
```sh
poetry install --with dev
```
3. Install pre-commit hooks
```sh
poetry run pre-commit install
```

Now whenever developing, enter virtual environment using
```sh
poetry shell
```
From now on this document assumes that you are within a virtual environment. Otherwise prepend you commands with `poetry run`.

### Testing

Tests are written in the `pytest` framework, to run them use:

```sh
pytest
```

To run extensive tests within isolated environments use `tox`:

```sh
tox
```

## Links

- [Change log](./CHANGELOG.md)
- [Contributing](./CONTRIBUTING.md)
