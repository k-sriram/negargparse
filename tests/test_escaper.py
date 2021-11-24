import pytest
from negargparse import negargparse

# Testing the RegexEscaper framework


@pytest.fixture
def HTMLescaper():
    return negargparse.RegexEscaper(
        [
            ("&", "&amp;"),
            ("<", "&lt;"),
            (">", "&gt;"),
            ('"', "&quot;"),
            ("'", "&#x27;"),
        ],
        [
            ("&#x27;", "'"),
            ("&quot;", '"'),
            ("&gt;", ">"),
            ("&lt;", "<"),
            ("&amp;", "&"),
        ],
    )


@pytest.mark.parametrize(
    "raw, escaped",
    [
        (
            '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">',
            "&lt;meta http-equiv=&quot;Content-Type&quot; content=&quot;text/html; charset=utf-8&quot;&gt;",
        ),
        (
            "&lt; & that &<  what '\"triple quoted\"'",
            "&amp;lt; &amp; that &amp;&lt;  what &#x27;&quot;triple quoted&quot;&#x27;",
        ),
    ],
)
def test_HTML_escaper(HTMLescaper, raw, escaped):
    assert HTMLescaper.escape(raw) == escaped
    assert HTMLescaper.unescape(escaped) == raw


@pytest.mark.parametrize(
    "raw, escaped",
    [
        ("argument", "argument"),
        ("-o", "-o"),
        ("-O3", "-O3"),
        ("-2", "\\-2"),
        ("-2fix", "\\-2fix"),
        ("-o -1", "-o -1"),
        ("-o\n-2", "-o\n-2"),
        (r"\-d", r"\-d"),
        (r"\-1", r"\\-1"),
        (r"\\\\-4", r"\\\\\-4"),
    ],
)
def test_negargescaper(raw, escaped):
    escaper = negargparse.NegativeArgumentParser.negargescaper
    assert escaper.escape(raw) == escaped
    assert escaper.unescape(escaped) == raw
