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
        pytest.param(
            '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">',
            "&lt;meta http-equiv=&quot;Content-Type&quot; content=&quot;text/html; charset=utf-8&quot;&gt;",
            id="1",
        ),
        pytest.param(
            "&lt; & that &<  what '\"triple quoted\"'",
            "&amp;lt; &amp; that &amp;&lt;  what &#x27;&quot;triple quoted&quot;&#x27;",
            id="2",
        ),
    ],
)
def test_HTML_escaper(HTMLescaper, raw, escaped):
    assert HTMLescaper.escape(raw) == escaped
    assert HTMLescaper.unescape(escaped) == raw


@pytest.mark.parametrize(
    "raw, escaped",
    [
        pytest.param("argument", "argument", id="simple_arg"),
        pytest.param("-o", "-o", id="simple_opt"),
        pytest.param("-O3", "-O3", id="digit_not_at_start"),
        pytest.param("-2", "\\-2", id="NegNumber"),
        pytest.param("-2fix", "\\-2fix", id="NegString"),
        pytest.param("-o -1", "-o -1", id="space_in_arg"),
        pytest.param("-o\n-2", "-o\n-2", id="newline_in_arg"),
        pytest.param(r"\-d", r"\-d", id="dont_reescape_string"),
        pytest.param(r"\-1", r"\\-1", id="reescape"),
        pytest.param(r"\\\\-4", r"\\\\\-4", id="multiple_reescape"),
    ],
)
def test_negargescaper(raw, escaped):
    escaper = negargparse.NegativeArgumentParser.negargescaper
    assert escaper.escape(raw) == escaped
    assert escaper.unescape(escaped) == raw
