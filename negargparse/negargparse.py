# negargparse.py
# Author: Sriram Krishna
# Created on: 2021-11-17

# MIT No Attribution License

# Copyright (c) 2021 Sriram Krishna

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Argument Parser which understands negative numbers"""

from __future__ import annotations

# Explicity stating version here so that module can be used independently.
# Concurrency between this and package version is maintained using test and
# commit hooks.
__version__ = "0.2.0.dev1"

__all__ = [
    "NegativeArgumentParser",
    "NegInt",
    "NegFloat",
    "NegString",
]

import re as _re
import sys as _sys

import argparse
from functools import partial
from typing import Callable, Protocol, Sequence, Type


class Escaper(Protocol):
    def escape(self, string: str) -> str:
        ...

    def unescape(self, string: str) -> str:
        ...


class RegexEscaper:
    def __init__(
        self, escapes: list[tuple[str, str]], unescapes: list[tuple[str, str]]
    ) -> None:
        self.escapes = self._compileescapes(escapes)
        self.unescapes = self._compileescapes(unescapes)

    @staticmethod
    def _compileescapes(
        escapetemplate: list[tuple[str, str]],
    ) -> list[Callable[[str], str]]:
        return [partial(_re.compile(et[0]).sub, sub=et[1]) for et in escapetemplate]

    @staticmethod
    def _substitute(string: str, escapes: list[Callable[[str], str]]) -> str:
        for escaper in escapes:
            string = escaper(string)
        return string

    def escape(self, string: str) -> str:
        return self._substitute(string, self.escapes)

    def unescape(self, string: str) -> str:
        return self._substitute(string, self.unescapes)


class NegativeArgumentParser(argparse.ArgumentParser):
    negargescaper: Escaper = RegexEscaper(
        [(r"\A(\\*-\d)", "\\\1")],
        [(r"\A\\(\\*-\d)", "\1")],
    )

    def parse_known_args(
        self,
        args: Sequence[str] = None,
        namespace: argparse.Namespace = None,
    ) -> tuple[argparse.Namespace, list[str]]:
        if args is None:
            # args default to the system args
            args = _sys.argv[1:]
        args = [self.negargescaper.escape(arg) for arg in args]
        return super().parse_known_args(args, namespace)


# Not explicitly checking for type of arg as it is only supposed
# to be called by argparse and it always provides a string.


class NegInt(int):
    def __new__(cls: Type[NegInt], arg: str) -> NegInt:
        arg = NegativeArgumentParser.negargescaper.unescape(arg)
        return super().__new__(cls, arg)


class NegFloat(float):
    def __new__(cls: Type[NegFloat], arg: str) -> NegFloat:
        arg = NegativeArgumentParser.negargescaper.unescape(arg)
        return super().__new__(cls, arg)


class NegString(str):
    def __new__(cls: Type[NegString], arg: str) -> NegString:
        arg = NegativeArgumentParser.negargescaper.unescape(arg)
        return super().__new__(cls, arg)
