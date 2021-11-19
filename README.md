# negargparse

An ArgumentParser which understands negative numbers.

---

_Usage section yet to be written._

## Development

### Setup development environment

Ensure you have poetry installed. You can get it from https://github.com/python-poetry/poetry. This requires poetry version >=1.2 which is currently only released as alpha.

1. Clone the repository
2. Install the package
```sh
poetry install
```
3. Install pre-commit hooks
```sh
poetry run pre-commit
```

Now whenever developing, enter virtual environment using
```sh
poetry shell
```
### As standalone module

While it can be used as a package, `negargparse` is intended to be usable as a standalone module as well. It is being developed as a package so as to be able to do automated quality control and testing which is harder to do for a module.

### Formatting and Linting

Formatting style is enforced by [black](https://black.readthedocs.io/en/stable/) and linting by [flake8](https://flake8.pycqa.org/en/latest/). These are parts of the pre-commit hook.

### Versioning style

The version format should follow [PEP 440](https://www.python.org/dev/peps/pep-0440/). This project follows a [semantic versioning scheme](https://semver.org/). Before version 1.0.0 breaking changes can be introduced in minor patches.

### Test-driven development

After version 0.2.0 the project shall follow test-driven development.

### Miscellaneous

[Gitmoji](https://gitmoji.dev/) is used to identify type of a commit.

On the [github repository](https://github.com/k-sriram/negargparse) there is a [project board](https://github.com/k-sriram/negargparse/projects/1) to track things to be done.
