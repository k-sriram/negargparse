"""Argument Parser which understands negative numbers"""

from __future__ import annotations

# Explicity stating version here so that module can be used independently.
# Concurrency between this and package version is maintained using test and
# commit hooks.
__version__ = "0.1.2"

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
from typing import Sequence, Type


_negsentinel = "__minussign__"
_negre = _re.compile(r"^-\d.*$")
_sentre = _re.compile(f"^{_negsentinel}")
_minus = r"-"


def sentinelise_args(args: list[str], sentinel: str = _negsentinel) -> None:
    for i, arg in enumerate(args):
        if _negre.fullmatch(arg) is not None:
            args[i] = f"{sentinel}{arg[1:]}"


class NegativeArgumentParser(argparse.ArgumentParser):
    def parse_known_args(
        self,
        args: Sequence[str] = None,
        namespace: argparse.Namespace = None,
    ) -> tuple[argparse.Namespace, list[str]]:
        if args is None:
            # args default to the system args
            args = _sys.argv[1:]
        else:
            # make sure that args are mutable
            args = list(args)
        sentinelise_args(args)
        return super().parse_known_args(args, namespace)


# Not explicitly checking for type of arg as it is only supposed
# to be called by argparse and it always provides a string.


class NegInt(int):
    def __new__(cls: Type[NegInt], arg: str) -> NegInt:
        arg = _sentre.sub(_minus, arg, count=1)
        return super().__new__(cls, arg)


class NegFloat(float):
    def __new__(cls: Type[NegFloat], arg: str) -> NegFloat:
        arg = _sentre.sub(_minus, arg, count=1)
        return super().__new__(cls, arg)


class NegString(str):
    def __new__(cls: Type[NegString], arg: str) -> NegString:
        arg = _sentre.sub(_minus, arg, count=1)
        return super().__new__(cls, arg)
