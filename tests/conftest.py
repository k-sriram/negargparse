# content of conftest.py
#
import sys
import pytest

ALL = set("darwin linux win32".split())


def pytest_runtest_setup(item):
    for mark in item.iter_markers(name="testvalid"):
        if sys.version_info[:2] != (3, 10):
            pytest.skip(
                "Running test validators only in 3.10 due to change in argparse behaviour"
            )
