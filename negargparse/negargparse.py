"""Argument Parser which understands negative numbers"""

__version__ = "0.1.0"

import re as _re
import sys as _sys

import argparse

_negsentinel = "__minussign__"
_negre = _re.compile(r"^-\d.*$")
_sentre = _re.compile(f"^{_negsentinel}")
_minus = r"-"


def sentinelise_args(args, sentinel=_negsentinel):
    for i, arg in enumerate(args):
        if _negre.fullmatch(arg) is not None:
            args[i] = f"{sentinel}{arg[1:]}"


class NegativeArgumentParser(argparse.ArgumentParser):
    def parse_known_args(self, args, namespace=None):
        if args is None:
            # args default to the system args
            args = _sys.argv[1:]
        else:
            # make sure that args are mutable
            args = list(args)
        sentinelise_args(args)
        return super().parse_known_args(args, namespace)


class NegInt(int):
    def __new__(cls, value):
        if isinstance(value, str):
            value = _sentre.sub(_minus, value, count=1)
        return super().__new__(value)


class NegFloat(float):
    def __new__(cls, value):
        if isinstance(value, str):
            value = _sentre.sub(_minus, value, count=1)
        return super().__new__(value)


class NegString(str):
    def __new__(cls, value):
        if isinstance(value, str):
            value = _sentre.sub(_minus, value, count=1)
        return super().__new__(value)
