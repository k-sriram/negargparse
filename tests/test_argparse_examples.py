import sys
from argparse import Namespace
import argparse
from textwrap import dedent
from functools import partial
from inspect import signature
import pytest
from negargparse.negargparse import NegativeArgumentParser, NegInt


@pytest.fixture
def example_1_parser():
    parser = NegativeArgumentParser(description="Process some integers.")
    parser.add_argument(
        "integers",
        metavar="N",
        type=int,
        nargs="+",
        help="an integer for the accumulator",
    )
    parser.add_argument(
        "--sum",
        dest="accumulate",
        action="store_const",
        const=sum,
        default=max,
        help="sum the integers (default: find the max)",
    )
    return parser


@pytest.mark.parametrize(
    "args, result",
    [
        (["1", "2", "3", "4"], 4),
        (["1", "2", "3", "4", "--sum"], 10),
    ],
)
def test_example_1(example_1_parser, args, result):
    args = example_1_parser.parse_args(args)
    assert args.accumulate(args.integers) == result


def test_example_1_helpmsg(example_1_parser, capsys):
    helpmsg = dedent(
        """\
        usage: prog.py [-h] [--sum] N [N ...]

        Process some integers.

        positional arguments:
          N           an integer for the accumulator

        options:
          -h, --help  show this help message and exit
          --sum       sum the integers (default: find the max)
        """
    )
    example_1_parser.prog = "prog.py"
    with pytest.raises(SystemExit):
        example_1_parser.parse_args(["-h"])
    capstd = capsys.readouterr()
    assert capstd.out == helpmsg


def test_example_1_invalid(example_1_parser, capsys):
    usage = dedent(
        """\
        usage: prog.py [-h] [--sum] N [N ...]
        prog.py: error: argument N: invalid int value: 'a'
        """
    )
    example_1_parser.prog = "prog.py"
    with pytest.raises(SystemExit):
        example_1_parser.parse_args(["a", "b", "c"])
    capstd = capsys.readouterr()
    assert capstd.err == usage


# ---------------- Comparison between argparse and negargparse ----------------

# ----------------------------------- Setup -----------------------------------


def compare_class_behavior(alias, class1, class2, expected):
    def ccbdecorator(func):
        def test_compare_class(*args, **kwargs):
            # Test whether provided class is used
            with pytest.raises(TypeError):
                func(*args, **kwargs, **{alias: None})
            func1 = partial(func, **{alias: class1})
            func2 = partial(func, **{alias: class2})
            assert (val1 := func1(*args, **kwargs)) == func2(*args, **kwargs)
            assert val1 == expected

        sig = signature(func)
        sig = sig.replace(
            parameters=(value for key, value in sig.parameters.items() if key != alias)
        )
        test_compare_class.__signature__ = sig
        test_compare_class.__name__ = func.__name__
        return test_compare_class

    return ccbdecorator


compare_AP = partial(
    compare_class_behavior, "AP", argparse.ArgumentParser, NegativeArgumentParser
)

# ----------------------------------- Tests -----------------------------------


@compare_AP(
    dedent(
        """\
    usage: myprogram [-h]

    options:
      -h, --help  show this help message and exit
    """
    )
)
def test_example_prog(AP, capsys):
    parser = AP(prog="myprogram")
    parser.print_help()
    return capsys.readouterr().out


@compare_AP(
    dedent(
        """\
        usage: PROG [-h] [--foo [FOO]] bar [bar ...]

        positional arguments:
          bar          bar help

        options:
          -h, --help   show this help message and exit
          --foo [FOO]  foo help
        """
    )
)
def test_example_usage(AP, capsys):
    parser = AP(prog="PROG")
    parser.add_argument("--foo", nargs="?", help="foo help")
    parser.add_argument("bar", nargs="+", help="bar help")
    parser.print_help()
    return capsys.readouterr().out


@compare_AP(
    dedent(
        """\
        usage: argparse.py [-h]

        A foo that bars

        options:
          -h, --help  show this help message and exit
        """
    )
)
def test_example_description(AP, capsys):
    parser = AP(prog="argparse.py", description="A foo that bars")
    parser.print_help()
    return capsys.readouterr().out


@compare_AP(
    dedent(
        """\
        usage: argparse.py [-h]

        A foo that bars

        options:
          -h, --help  show this help message and exit

        And that's how you'd foo a bar
        """
    )
)
def test_example_epilog(AP, capsys):
    parser = AP(
        prog="argparse.py",
        description="A foo that bars",
        epilog="And that's how you'd foo a bar",
    )
    parser.print_help()
    return capsys.readouterr().out


@compare_AP([Namespace(foo="XXX", parent=2), Namespace(bar="YYY", parent=None)])
def test_example_parents(AP):
    retval = []

    parent_parser = AP(add_help=False)
    parent_parser.add_argument("--parent", type=int)

    foo_parser = AP(parents=[parent_parser])
    foo_parser.add_argument("foo")
    retval.append(foo_parser.parse_args(["--parent", "2", "XXX"]))

    bar_parser = AP(parents=[parent_parser])
    bar_parser.add_argument("--bar")
    retval.append(bar_parser.parse_args(["--bar", "YYY"]))

    return retval


@compare_AP(
    dedent(
        """\
        usage: PROG [-h]

        Please do not mess up this text!
        --------------------------------
            I have indented it
            exactly the way
            I want it

        options:
          -h, --help  show this help message and exit
        """
    )
)
def test_example_formatter_class(AP, capsys):
    parser = AP(
        prog="PROG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=dedent(
            """\
            Please do not mess up this text!
            --------------------------------
                I have indented it
                exactly the way
                I want it
            """
        ),
    )
    parser.print_help()
    return capsys.readouterr().out


@compare_AP(
    dedent(
        """\
        usage: PROG [-h] [--foo FOO] [bar ...]

        positional arguments:
          bar         BAR! (default: [1, 2, 3])

        options:
          -h, --help  show this help message and exit
          --foo FOO   FOO! (default: 42)
        """
    )
)
def test_example_ArgumentDefaultsHelpFormatter(AP, capsys):
    parser = AP(prog="PROG", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--foo", type=int, default=42, help="FOO!")
    parser.add_argument("bar", nargs="*", default=[1, 2, 3], help="BAR!")
    parser.print_help()
    return capsys.readouterr().out


@compare_AP(
    dedent(
        """\
        usage: PROG [-h] [--foo int] float

        positional arguments:
          float

        options:
          -h, --help  show this help message and exit
          --foo int
        """
    )
)
def test_example_MetavarTypeHelpFormatter(AP, capsys):
    parser = AP(prog="PROG", formatter_class=argparse.MetavarTypeHelpFormatter)
    parser.add_argument("--foo", type=int)
    parser.add_argument("bar", type=float)
    parser.print_help()
    return capsys.readouterr().out


@compare_AP(Namespace(bar="Y", f="X"))
def test_example_prefix_chars(AP):
    parser = AP(prog="PROG", prefix_chars="-+")
    parser.add_argument("+f")
    parser.add_argument("++bar")
    return parser.parse_args("+f X ++bar Y".split())


@compare_AP(Namespace(f="bar"))
def test_example_fromfile_prefix_chars(AP, tmp_path):
    filepath = tmp_path / "args.txt"
    with filepath.open("w") as fp:
        fp.write("-f\nbar")
    parser = AP(fromfile_prefix_chars="@")
    parser.add_argument("-f")
    return parser.parse_args(["-f", "foo", f"@{filepath}"])


@compare_AP([Namespace(bar="BAR", foo="1"), Namespace()])
def test_example_argument_default(AP):
    retval = []

    parser = AP(argument_default=argparse.SUPPRESS)
    parser.add_argument("--foo")
    parser.add_argument("bar", nargs="?")

    retval.append(parser.parse_args(["--foo", "1", "BAR"]))
    retval.append(parser.parse_args([]))

    return retval


if sys.version_info >= (3, 5):

    @compare_AP(
        dedent(
            """\
            usage: PROG [-h] [--foobar] [--foonley]
            PROG: error: unrecognized arguments: --foon
            """
        )
    )
    def test_example_allow_abbrev(AP, capsys):
        parser = AP(prog="PROG", allow_abbrev=False)
        parser.add_argument("--foobar", action="store_true")
        parser.add_argument("--foonley", action="store_false")
        with pytest.raises(SystemExit):
            parser.parse_args(["--foon"])
        return capsys.readouterr().err

    @compare_AP(Namespace(foobar=False, foonley=False))
    def test_example_allow_abbrev_true(AP):
        parser = AP(prog="PROG", allow_abbrev=True)
        parser.add_argument("--foobar", action="store_true")
        parser.add_argument("--foonley", action="store_false")
        return parser.parse_args(["--foon"])


@compare_AP(
    dedent(
        """\
        usage: PROG [-h] [-f FOO] [--foo FOO]

        options:
          -h, --help  show this help message and exit
          -f FOO      old foo help
          --foo FOO   new foo help
        """
    )
)
def test_example_conflict_handler(AP, capsys):
    parser = AP(prog="PROG", conflict_handler="resolve")
    parser.add_argument("-f", "--foo", help="old foo help")
    parser.add_argument("--foo", help="new foo help")
    parser.print_help()
    capstd = capsys.readouterr()
    return capstd.out


@compare_AP(
    dedent(
        """\
        usage: myprogram.py [-h] [--foo FOO]

        options:
          -h, --help  show this help message and exit
          --foo FOO   foo help
        """
    )
)
def test_example_add_help_1(AP, capsys):
    parser = AP(prog="myprogram.py")
    parser.add_argument("--foo", help="foo help")
    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])
    return capsys.readouterr().out


@compare_AP(
    dedent(
        """\
        usage: PROG [--foo FOO]

        options:
          --foo FOO  foo help
        """
    )
)
def test_example_add_help_2(AP, capsys):
    parser = AP(prog="PROG", add_help=False)
    parser.add_argument("--foo", help="foo help")
    parser.print_help()
    return capsys.readouterr().out


@compare_AP(
    dedent(
        """\
        usage: PROG [+h]

        options:
          +h, ++help  show this help message and exit
        """
    )
)
def test_example_add_help_3(AP, capsys):
    parser = AP(prog="PROG", prefix_chars="+/")
    parser.print_help()
    return capsys.readouterr().out


if sys.version_info >= (3, 9):

    @compare_AP("Catching an argumentError\n")
    def test_example_exit_on_error(AP, capsys):
        parser = AP(exit_on_error=False)
        parser.add_argument("--integers", type=NegInt)
        try:
            parser.parse_args("--integers a".split())
        except argparse.ArgumentError:
            print("Catching an argumentError")
        return capsys.readouterr().out


@compare_AP(
    [
        Namespace(bar="BAR", foo=None),
        Namespace(bar="BAR", foo="FOO"),
        dedent(
            """\
        usage: PROG [-h] [-f FOO] bar
        PROG: error: the following arguments are required: bar
        """
        ),
    ]
)
def test_example_add_argument_name(AP, capsys):
    retval = []
    parser = AP(prog="PROG")
    parser.add_argument("-f", "--foo")
    parser.add_argument("bar")
    retval.append(parser.parse_args(["BAR"]))
    retval.append(parser.parse_args(["BAR", "--foo", "FOO"]))
    with pytest.raises(SystemExit):
        parser.parse_args(["--foo", "FOO"])
    retval.append(capsys.readouterr().err)
    return retval


@compare_AP(Namespace(foo="1"))
def test_example_add_argument_action_store(AP):
    parser = AP()
    parser.add_argument("--foo")
    return parser.parse_args("--foo 1".split())


@compare_AP(Namespace(foo=42))
def test_example_add_argument_action_store_const(AP):
    parser = AP()
    parser.add_argument("--foo", action="store_const", const=42)
    return parser.parse_args(["--foo"])


@compare_AP(Namespace(foo=True, bar=False, baz=True))
def test_example_add_argument_action_store_bool(AP):
    parser = AP()
    parser.add_argument("--foo", action="store_true")
    parser.add_argument("--bar", action="store_false")
    parser.add_argument("--baz", action="store_false")
    return parser.parse_args("--foo --bar".split())


@compare_AP(Namespace(foo=["1", "2"]))
def test_example_add_argument_action_append(AP):
    parser = AP()
    parser.add_argument("--foo", action="append")
    return parser.parse_args("--foo 1 --foo 2".split())


@compare_AP(Namespace(types=[str, int]))
def test_example_add_argument_action_append_const(AP):
    parser = AP()
    parser.add_argument("--str", dest="types", action="append_const", const=str)
    parser.add_argument("--int", dest="types", action="append_const", const=int)
    return parser.parse_args("--str --int".split())


@compare_AP(Namespace(verbose=3))
def test_example_add_argument_action_count(AP):
    parser = AP()
    parser.add_argument("--verbose", "-v", action="count", default=0)
    return parser.parse_args(["-vvv"])


@compare_AP("PROG 2.0\n")
def test_example_add_argument_action_version(AP, capsys):
    parser = AP(prog="PROG")
    parser.add_argument("--version", action="version", version="%(prog)s 2.0")
    with pytest.raises(SystemExit):
        parser.parse_args(["--version"])
    return capsys.readouterr().out


if sys.version_info >= (3, 8):

    @compare_AP(Namespace(foo=["f1", "f2", "f3", "f4"]))
    def test_example_add_argument_action_extend(AP):
        parser = AP()
        parser.add_argument("--foo", action="extend", nargs="+", type=str)
        return parser.parse_args(["--foo", "f1", "--foo", "f2", "f3", "f4"])


if sys.version_info >= (3, 9):

    @compare_AP(Namespace(foo=False))
    def test_example_add_argument_action_BooleanOptionalAction(AP):
        parser = AP()
        parser.add_argument("--foo", action=argparse.BooleanOptionalAction)
        return parser.parse_args(["--no-foo"])

    @compare_AP(
        [
            dedent(
                """\
                Namespace(foo=None, bar=None) '1' None
                Namespace(foo=None, bar='1') '2' '--foo'
                """
            ),
            Namespace(bar="1", foo="2"),
        ]
    )
    def test_example_add_argument_action_customFooAction(AP, capsys):
        class FooAction(argparse.Action):
            def __init__(self, option_strings, dest, nargs=None, **kwargs):
                if nargs is not None:
                    raise ValueError("nargs not allowed")
                super().__init__(option_strings, dest, **kwargs)

            def __call__(self, parser, namespace, values, option_string=None):
                print("%r %r %r" % (namespace, values, option_string))
                setattr(namespace, self.dest, values)

        parser = AP()
        parser.add_argument("--foo", action=FooAction)
        parser.add_argument("bar", action=FooAction)
        args = parser.parse_args("1 --foo 2".split())
        retval = []
        retval.append(capsys.readouterr().out)
        retval.append(args)
        return retval


@compare_AP(Namespace(bar=["c"], foo=["a", "b"]))
def test_example_add_argument_nargs_N(AP):
    parser = AP()
    parser.add_argument("--foo", nargs=2)
    parser.add_argument("bar", nargs=1)
    return parser.parse_args("c --foo a b".split())


@compare_AP(
    [
        Namespace(bar="XX", foo="YY"),
        Namespace(bar="XX", foo="c"),
        Namespace(bar="d", foo="d"),
    ]
)
def test_example_add_argument_nargs_questionmark(AP):
    parser = AP()
    parser.add_argument("--foo", nargs="?", const="c", default="d")
    parser.add_argument("bar", nargs="?", default="d")
    retval = []
    retval.append(parser.parse_args(["XX", "--foo", "YY"]))
    retval.append(parser.parse_args(["XX", "--foo"]))
    retval.append(parser.parse_args([]))
    return retval


@compare_AP(Namespace(bar=["1", "2"], baz=["a", "b"], foo=["x", "y"]))
def test_example_add_argument_nargs_star(AP):
    parser = AP()
    parser.add_argument("--foo", nargs="*")
    parser.add_argument("--bar", nargs="*")
    parser.add_argument("baz", nargs="*")
    return parser.parse_args("a b --foo x y --bar 1 2".split())


@compare_AP(
    [
        Namespace(foo=["a", "b"]),
        dedent(
            """\
            usage: PROG [-h] foo [foo ...]
            PROG: error: the following arguments are required: foo
            """
        ),
    ]
)
def test_example_add_argument_nargs_plus(AP, capsys):
    parser = AP(prog="PROG")
    parser.add_argument("foo", nargs="+")
    retval = []
    retval.append(parser.parse_args(["a", "b"]))
    with pytest.raises(SystemExit):
        parser.parse_args([])
    retval.append(capsys.readouterr().err)
    return retval


@compare_AP(
    [
        Namespace(foo="2"),
        Namespace(foo=42),
    ]
)
def test_example_add_argument_default_1(AP):
    parser = AP()
    parser.add_argument("--foo", default=42)
    retval = []
    retval.append(parser.parse_args(["--foo", "2"]))
    retval.append(parser.parse_args([]))
    return retval


@compare_AP(Namespace(foo=101))
def test_example_add_argument_default_2(AP):
    parser = AP()
    parser.add_argument("--foo", default=42)
    return parser.parse_args([], namespace=argparse.Namespace(foo=101))


@compare_AP(Namespace(length=10, width=10.5))
def test_example_add_argument_default_3(AP):
    parser = AP()
    parser.add_argument("--length", default="10", type=int)
    parser.add_argument("--width", default=10.5, type=int)
    return parser.parse_args([])


@compare_AP([Namespace(foo="a"), Namespace(foo=42)])
def test_example_add_argument_default_4(AP):
    parser = AP()
    parser.add_argument("foo", nargs="?", default=42)
    retval = []
    retval.append(parser.parse_args(["a"]))
    retval.append(parser.parse_args([]))
    return retval


@compare_AP([Namespace(), Namespace(foo="1")])
def test_example_add_argument_default_5(AP):
    parser = AP()
    parser.add_argument("--foo", default=argparse.SUPPRESS)
    retval = []
    retval.append(parser.parse_args([]))
    retval.append(parser.parse_args(["--foo", "1"]))
    return retval


@compare_AP(Namespace(short_title='"the-tale-of-two-citi'))
def test_example_add_argument_type(AP):
    def hyphenated(string):
        return "-".join([word[:4] for word in string.casefold().split()])

    parser = AP()
    parser.add_argument("short_title", type=hyphenated)
    return parser.parse_args(['"The Tale of Two Cities"'])


@compare_AP(
    [
        Namespace(move="rock"),
        dedent(
            """\
            usage: game.py [-h] {rock,paper,scissors}
            game.py: error: argument move: invalid choice: 'fire' (choose from 'rock', 'paper', 'scissors')
            """
        ),
    ]
)
def test_example_add_argument_choices_1(AP, capsys):
    parser = AP(prog="game.py")
    parser.add_argument("move", choices=["rock", "paper", "scissors"])
    retval = []
    retval.append(parser.parse_args(["rock"]))
    with pytest.raises(SystemExit):
        parser.parse_args(["fire"])
    retval.append(capsys.readouterr().err)
    return retval


@compare_AP(
    [
        Namespace(door=3),
        dedent(
            """\
            usage: doors.py [-h] {1,2,3}
            doors.py: error: argument door: invalid choice: 4 (choose from 1, 2, 3)
            """
        ),
    ]
)
def test_example_add_argument_choices_2(AP, capsys):
    parser = AP(prog="doors.py")
    parser.add_argument("door", type=int, choices=range(1, 4))
    retval = []
    retval.append(parser.parse_args(["3"]))
    with pytest.raises(SystemExit):
        parser.parse_args(["4"])
    retval.append(capsys.readouterr().err)
    return retval


@compare_AP(
    [
        Namespace(foo="BAR"),
        dedent(
            """\
            usage: required.py [-h] --foo FOO
            required.py: error: the following arguments are required: --foo
            """
        ),
    ]
)
def test_example_add_argument_required(AP, capsys):
    parser = AP(prog="required.py")
    parser.add_argument("--foo", required=True)
    retval = []
    retval.append(parser.parse_args(["--foo", "BAR"]))
    with pytest.raises(SystemExit):
        parser.parse_args([])
    retval.append(capsys.readouterr().err)
    return retval


@compare_AP(
    dedent(
        """\
        usage: frobble [-h] [--foo] bar [bar ...]

        positional arguments:
          bar         one of the bars to be frobbled

        options:
          -h, --help  show this help message and exit
          --foo       foo the bars before frobbling
        """
    )
)
def test_example_add_argument_help_1(AP, capsys):
    parser = AP(prog="frobble")
    parser.add_argument(
        "--foo", action="store_true", help="foo the bars before frobbling"
    )
    parser.add_argument("bar", nargs="+", help="one of the bars to be frobbled")
    with pytest.raises(SystemExit):
        parser.parse_args(["-h"])
    return capsys.readouterr().out


@compare_AP(
    dedent(
        """\
        usage: frobble [-h] [bar]

        positional arguments:
          bar         the bar to frobble (default: 42)

        options:
          -h, --help  show this help message and exit
        """
    )
)
def test_example_add_argument_help_2(AP, capsys):
    parser = AP(prog="frobble")
    parser.add_argument(
        "bar",
        nargs="?",
        type=int,
        default=42,
        help="the bar to %(prog)s (default: %(default)s)",
    )
    parser.print_help()
    return capsys.readouterr().out


@compare_AP(
    dedent(
        """\
        usage: frobble [-h]

        options:
          -h, --help  show this help message and exit
        """
    )
)
def test_example_add_argument_help_3(AP, capsys):
    parser = AP(prog="frobble")
    parser.add_argument("--foo", help=argparse.SUPPRESS)
    parser.print_help()
    return capsys.readouterr().out


@compare_AP(
    [
        Namespace(foo="Y", bar="X"),
        dedent(
            """\
            usage: [-h] [--foo YYY] XXX

            positional arguments:
              XXX

            options:
              -h, --help  show this help message and exit
              --foo YYY
            """
        ),
    ]
)
def test_example_add_argument_metavar(AP, capsys):
    parser = AP(prog="")
    parser.add_argument("--foo", metavar="YYY")
    parser.add_argument("bar", metavar="XXX")
    retval = []
    retval.append(parser.parse_args("X --foo Y".split()))
    parser.print_help()
    retval.append(capsys.readouterr().out)
    return retval


@compare_AP(
    dedent(
        """\
        usage: PROG [-h] [-x X X] [--foo bar baz]

        options:
          -h, --help     show this help message and exit
          -x X X
          --foo bar baz
        """
    )
)
def test_example_add_argument_metavar_nargs(AP, capsys):
    parser = AP(prog="PROG")
    parser.add_argument("-x", nargs=2)
    parser.add_argument("--foo", nargs=2, metavar=("bar", "baz"))
    parser.print_help()
    return capsys.readouterr().out


@compare_AP([Namespace(foo_bar="1", x="2"), Namespace(foo_bar="1", x="2")])
def test_example_add_argument_nodest(AP):
    parser = AP()
    parser.add_argument("-f", "--foo-bar", "--foo")
    parser.add_argument("-x", "-y")
    retval = []
    retval.append(parser.parse_args("-f 1 -x 2".split()))
    retval.append(parser.parse_args("--foo 1 -y 2".split()))
    return retval


@compare_AP(Namespace(bar="XXX"))
def test_example_add_argument(AP):
    parser = AP()
    parser.add_argument("--foo", dest="bar")
    return parser.parse_args("--foo XXX".split())


@compare_AP(
    [
        Namespace(foo=None, x="X"),
        Namespace(foo="FOO", x=None),
        Namespace(foo="FOO", x=None),
        Namespace(foo=None, x="X"),
    ]
)
def test_example_parse_args_ovs_1(AP):
    parser = AP(prog="PROG")
    parser.add_argument("-x")
    parser.add_argument("--foo")
    retval = []
    retval.append(parser.parse_args(["-x", "X"]))
    retval.append(parser.parse_args(["--foo", "FOO"]))
    retval.append(parser.parse_args(["--foo=FOO"]))
    retval.append(parser.parse_args(["-xX"]))
    return retval


@compare_AP(Namespace(x=True, y=True, z="Z"))
def test_example_parse_args_joinshortargs(AP):
    parser = AP(prog="PROG")
    parser.add_argument("-x", action="store_true")
    parser.add_argument("-y", action="store_true")
    parser.add_argument("-z")
    return parser.parse_args(["-xyzZ"])


@compare_AP(
    [
        dedent(
            """\
            usage: PROG [-h] [--foo FOO] [bar]
            PROG: error: argument --foo: invalid int value: 'spam'
            """
        ),
        dedent(
            """\
            usage: PROG [-h] [--foo FOO] [bar]
            PROG: error: unrecognized arguments: --bar
            """
        ),
        dedent(
            """\
            usage: PROG [-h] [--foo FOO] [bar]
            PROG: error: unrecognized arguments: badger
            """
        ),
    ]
)
def test_example_parse_args_invalid_arguments(AP, capsys):
    parser = AP(prog="PROG")
    parser.add_argument("--foo", type=int)
    parser.add_argument("bar", nargs="?")
    retval = []
    with pytest.raises(SystemExit):
        parser.parse_args(["--foo", "spam"])
    retval.append(capsys.readouterr().err)
    with pytest.raises(SystemExit):
        parser.parse_args(["--bar"])
    retval.append(capsys.readouterr().err)
    with pytest.raises(SystemExit):
        parser.parse_args(["spam", "badger"])
    retval.append(capsys.readouterr().err)
    return retval


@compare_AP(
    [
        Namespace(bacon="MMM", badger=None),
        Namespace(bacon=None, badger="WOOD"),
        dedent(
            """\
            usage: PROG [-h] [-bacon BACON] [-badger BADGER]
            PROG: error: ambiguous option: -ba could match -bacon, -badger
            """
        ),
    ]
)
def test_example_parse_args_prefix_matching(AP, capsys):
    parser = AP(prog="PROG")
    parser.add_argument("-bacon")
    parser.add_argument("-badger")
    retval = []
    retval.append(parser.parse_args("-bac MMM".split()))
    retval.append(parser.parse_args("-bad WOOD".split()))
    with pytest.raises(SystemExit):
        parser.parse_args("-ba BA".split())
    retval.append(capsys.readouterr().err)
    return retval


@compare_AP((Namespace(bar="BAR", foo=True), ["--badger", "spam"]))
def test_example_parse_known_args(AP):
    parser = AP()
    parser.add_argument("--foo", action="store_true")
    parser.add_argument("bar")
    return parser.parse_known_args(["--foo", "--badger", "BAR", "spam"])


if sys.version_info >= (3, 7):

    @compare_AP(
        [
            (Namespace(cmd="doit", foo="bar", rest=[1]), ["2", "3"]),
            Namespace(cmd="doit", foo="bar", rest=[1, 2, 3]),
        ]
    )
    def test_example_parse_intermixed_args(AP):
        parser = AP()
        parser.add_argument("--foo")
        parser.add_argument("cmd")
        parser.add_argument("rest", nargs="*", type=int)
        retval = []
        retval.append(parser.parse_known_args("doit 1 --foo bar 2 3".split()))
        retval.append(parser.parse_intermixed_args("doit 1 --foo bar 2 3".split()))
        return retval


# ------------------------------------ End ------------------------------------


@pytest.fixture(scope="module")
def negarg_parser_1_AP():
    parser = argparse.ArgumentParser(prog="PROG")
    parser.add_argument("-x")
    parser.add_argument("foo", nargs="?")
    return parser


def test_example_negarg_1_AP(negarg_parser_1_AP):
    assert negarg_parser_1_AP.parse_args(["-x", "-1"]) == Namespace(foo=None, x="-1")


def test_example_negarg_2_AP(negarg_parser_1_AP):
    assert negarg_parser_1_AP.parse_args(["-x", "-1", "-5"]) == Namespace(
        foo="-5", x="-1"
    )


@pytest.fixture(scope="module")
def negarg_parser_2_AP():
    parser = argparse.ArgumentParser(prog="PROG")
    parser.add_argument("-1", dest="one")
    parser.add_argument("foo", nargs="?")
    return parser


def test_example_negarg_3_AP(negarg_parser_2_AP):
    assert negarg_parser_2_AP.parse_args(["-1", "X"]) == Namespace(foo=None, one="X")


def test_example_negarg_4_AP(negarg_parser_2_AP, capsys):
    with pytest.raises(SystemExit):
        negarg_parser_2_AP.parse_args(["-2"])
    assert capsys.readouterr().err == dedent(
        """\
        usage: PROG [-h] [-1 ONE] [foo]
        PROG: error: unrecognized arguments: -2
        """
    )


def test_example_negarg_5_AP(negarg_parser_2_AP, capsys):
    with pytest.raises(SystemExit):
        negarg_parser_2_AP.parse_args(["-1", "-1"])
    assert capsys.readouterr().err == dedent(
        """\
        usage: PROG [-h] [-1 ONE] [foo]
        PROG: error: argument -1: expected one argument
        """
    )


@pytest.fixture(scope="module")
def negarg_parser_1_NAP():
    parser = NegativeArgumentParser(prog="PROG")
    parser.add_argument("-x")
    parser.add_argument("foo", nargs="?")
    return parser


@pytest.mark.xfail(reason="intended")
def test_example_negarg_1_NAP(negarg_parser_1_NAP):
    assert negarg_parser_1_NAP.parse_args(["-x", "-1"]) == Namespace(foo=None, x="-1")


@pytest.mark.xfail(reason="intended")
def test_example_negarg_2_NAP(negarg_parser_1_NAP):
    assert negarg_parser_1_NAP.parse_args(["-x", "-1", "-5"]) == Namespace(
        foo="-5", x="-1"
    )


@pytest.fixture(scope="module")
def negarg_parser_2_NAP():
    parser = NegativeArgumentParser(prog="PROG")
    parser.add_argument("-1", dest="one")
    parser.add_argument("foo", nargs="?")
    return parser


@pytest.mark.xfail(reason="intended")
def test_example_negarg_3_NAP(negarg_parser_2_NAP):
    assert negarg_parser_2_NAP.parse_args(["-1", "X"]) == Namespace(foo=None, one="X")


@pytest.mark.xfail(reason="intended")
def test_example_negarg_4_NAP(negarg_parser_2_NAP, capsys):
    with pytest.raises(SystemExit):
        negarg_parser_2_NAP.parse_args(["-2"])
    assert capsys.readouterr().err == dedent(
        """\
        usage: PROG [-h] [-1 ONE] [foo]
        PROG: error: unrecognized arguments: -2
        """
    )


@pytest.mark.xfail(reason="intended")
def test_example_negarg_5_NAP(negarg_parser_2_NAP, capsys):
    with pytest.raises(SystemExit):
        negarg_parser_2_NAP.parse_args(["-1", "-1"])
    assert capsys.readouterr().err == dedent(
        """\
        usage: PROG [-h] [-1 ONE] [foo]
        PROG: error: argument -1: expected one argument
        """
    )
