"""Argument Parser which understands negative numbers"""

from __future__ import annotations

__version__ = "0.1.1"
__all__ = [
    "sentinelise_args",
    "NegativeArgumentParser",
    "NegInt",
    "NegFloat",
    "NegString",
]

import re as _re
import sys as _sys

import argparse

from typing import TYPE_CHECKING as _TYPE_CHECKING

if _TYPE_CHECKING:
    from typing import (
        Optional,
        Sequence,
        Type,
        TypeVar,
    )

_T = TypeVar("_T")

_negsentinel = "__minussign__"
_negre = _re.compile(r"^-\d.*$")
_sentre = _re.compile(f"^{_negsentinel}")
_minus = r"-"


def sentinelise_args(args: list[str], sentinel: Optional[str] = _negsentinel) -> None:
    for i, arg in enumerate(args):
        if _negre.fullmatch(arg) is not None:
            args[i] = f"{sentinel}{arg[1:]}"


class NegativeArgumentParser(argparse.ArgumentParser):
    def parse_known_args(
        self,
        args: Optional[Sequence[str]] = None,
        namespace: Optional[argparse.Namespace] = None,
    ) -> tuple[argparse.Namespace, list[str]]:
        if args is None:
            # args default to the system args
            args = _sys.argv[1:]
        else:
            # make sure that args are mutable
            args = list(args)
        sentinelise_args(args)
        return super().parse_known_args(args, namespace)


# ignoring static type checking errors in the calling the __new__ functions
# Known bug in mypy while calling static/class methods using super
# See https://github.com/python/mypy/issues/9282

# Also not explicitly checking for type of arg as it is only supposed
# to be called by argparse and it always provides a string.


class NegInt(int):
    def __new__(cls: Type[NegInt], arg: str) -> NegInt:
        arg = _sentre.sub(_minus, arg, count=1)
        return super().__new__(cls, arg)  # type: ignore[misc]


class NegFloat(float):
    def __new__(cls: Type[NegFloat], arg: str) -> NegFloat:
        arg = _sentre.sub(_minus, arg, count=1)
        return super().__new__(cls, arg)  # type: ignore[misc]


class NegString(str):
    def __new__(cls: Type[NegString], arg: str) -> NegString:
        arg = _sentre.sub(_minus, arg, count=1)
        return super().__new__(cls, arg)  # type: ignore[misc]
