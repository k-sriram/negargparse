import re

try:
    from importlib import metadata
except ImportError:
    import importlib_metadata as metadata  # type: ignore
from negargparse import negargparse

_PACKAGE = "negargparse"

VERSION_PATTERN = r"""
    v?
    (?:
        (?:(?P<epoch>[0-9]+)!)?                           # epoch
        (?P<release>[0-9]+(?:\.[0-9]+)*)                  # release segment
        (?P<pre>                                          # pre-release
            [-_\.]?
            (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))
            [-_\.]?
            (?P<pre_n>[0-9]+)?
        )?
        (?P<post>                                         # post release
            (?:-(?P<post_n1>[0-9]+))
            |
            (?:
                [-_\.]?
                (?P<post_l>post|rev|r)
                [-_\.]?
                (?P<post_n2>[0-9]+)?
            )
        )?
        (?P<dev>                                          # dev release
            [-_\.]?
            (?P<dev_l>dev)
            [-_\.]?
            (?P<dev_n>[0-9]+)?
        )?
    )
    (?:\+(?P<local>[a-z0-9]+(?:[-_\.][a-z0-9]+)*))?       # local version
"""
VERSIONREGEX = re.compile(
    r"^\s*" + VERSION_PATTERN + r"\s*$",
    re.VERBOSE | re.IGNORECASE,
)


class PEP440Error(Exception):
    pass


def normalize(
    version,
):
    m = VERSIONREGEX.match(version)
    if m is None:
        raise PEP440Error(f"{version} does not meet PEP 440")
    gd = m.groupdict()
    epoch = f"{gd['epoch']}!" if gd["epoch"] is not None else ""
    release = gd["release"]
    if gd["pre"] is not None:
        pre_l = {
            "a": "a",
            "b": "b",
            "rc": "rc",
            "alpha": "a",
            "beta": "b",
            "c": "rc",
            "pre": "rc",
            "preview": "rc",
        }[gd["pre_l"].lower()]
        pre_n = int(gd["pre_n"]) or 0
        pre = f"{pre_l}{pre_n}"
    else:
        pre = ""
    if gd["post"] is not None:
        post_l = "post"
        if gd["post_n1"] is not None:
            post_n = int(gd["post_n1"])
        else:
            post_n = int(gd["post_n2"]) or 0
        post = f".{post_l}{post_n}"
    else:
        post = ""
    dev = f".dev{int(gd['dev_n']) or 0}" if gd["dev"] is not None else ""
    local = (
        f"+{gd['local'].replace('-','.').replace('_','.')}"
        if gd["local"] is not None
        else ""
    )
    return f"{epoch}{release}{pre}{post}{dev}{local}"


def test_version():
    # This test may also fail if package was not reinstalled, as
    # a dev-install doesn't update metadata on the fly.
    modver = negargparse.__version__
    modver = normalize(modver)
    pkgver = metadata.version(_PACKAGE)
    pkgver = normalize(pkgver)
    assert modver == pkgver
