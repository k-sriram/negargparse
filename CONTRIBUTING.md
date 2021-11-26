# Contributing

Contributions are welcome to this project. If you see a bug or want to suggest an improvement, file an [issue](https://github.com/k-sriram/aeqw/issues). Want to contribute code or documentation, open a [pull request](https://github.com/k-sriram/aeqw/pulls).

## Guidelines

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Gitmoji](https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg)](https://gitmoji.dev)
[![versioning: semver](https://img.shields.io/badge/versioning-semver-white)](https://semver.org)


### As standalone module

While it can be used as a package, `negargparse` is shoulod be usable as a standalone module as well. So any core features should be in the [`negargparse.py`](negargparse/negargparse.py). It is being developed as a package so as to be able to do automated quality control and testing which is harder to do for a module.

### Formatting and Linting

Formatting style is enforced by [`black`](https://black.readthedocs.io/en/stable/) and linting by [`flake8`](https://flake8.pycqa.org/en/latest/). These are parts of the pre-commit hook.

### Static type checking

The module should provide support for static type checking. [`mypy`](https://mypy.readthedocs.io/en/stable/index.html) is being used to check if the typing is internally consistent.

### Versioning style

The version format should follow [PEP 440](https://www.python.org/dev/peps/pep-0440/). This project follows a [semantic versioning scheme](https://semver.org/). Before version 1.0.0 breaking changes can be introduced in minor patches.

### Test-driven development

The project follows test-driven development.

### Miscellaneous

[Gitmoji](https://gitmoji.dev/) is used to identify type of a commit.

On the [github repository](https://github.com/k-sriram/negargparse) there is a [project board](https://github.com/k-sriram/negargparse/projects/1) to track things to be done.
