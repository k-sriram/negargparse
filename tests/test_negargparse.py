from textwrap import dedent
import pytest
from argparse import Namespace
from negargparse.negargparse import NegativeArgumentParser, NegInt, NegFloat, NegString


# test inspired from examples
@pytest.fixture
def example_1_negparser():
    parser = NegativeArgumentParser(description="Process some integers.")
    parser.add_argument(
        "integers",
        metavar="N",
        type=NegInt,
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
        (["1", "-2", "3", "4"], 4),
        (["1", "-2", "3", "4", "--sum"], 6),
        (["-1", "-2"], -1),
    ],
)
def test_example_1(example_1_negparser, args, result):
    args = example_1_negparser.parse_args(args)
    assert args.accumulate(args.integers) == result


#########


def test_example_negarg_1_NAP_revised():
    parser = NegativeArgumentParser(prog="PROG")
    parser.add_argument("-x", type=NegString)
    parser.add_argument("foo", nargs="?", type=NegString)
    assert parser.parse_args(["-x", "-1"]) == Namespace(foo=None, x="-1")


@pytest.mark.xfail(reason="possible feature")
def test_example_negarg_2_NAP_revised_autonegstring():
    parser = NegativeArgumentParser(prog="PROG")
    parser.add_argument("-x")
    parser.add_argument("foo", nargs="?")
    assert parser.parse_args(["-x", "-1", "-5"]) == Namespace(foo="-5", x="-1")


def test_example_negarg_2_NAP_revised():
    parser = NegativeArgumentParser(prog="PROG")
    parser.add_argument("-x", type=NegString)
    parser.add_argument("foo", nargs="?", type=NegString)
    assert parser.parse_args(["-x", "-1", "-5"]) == Namespace(foo="-5", x="-1")


# no implementation for test_example_negarg_2_NAP_revised


def test_example_negarg_4_NAP_revised():
    parser = NegativeArgumentParser(prog="PROG")
    parser.add_argument("-1", dest="one")
    parser.add_argument("foo", nargs="?", type=NegString)
    parser.parse_args(["-2"]) == Namespace(foo="-2", one=None)


@pytest.mark.xfail(reason="possible feature")
def test_example_negarg_5_NAP_revised(negarg_parser_2_NAP, capsys):
    parser = NegativeArgumentParser(prog="PROG")
    parser.add_argument("-1", dest="one", type=NegString)
    parser.add_argument("foo", nargs="?", type=NegString)

    with pytest.raises(SystemExit):
        negarg_parser_2_NAP.parse_args(["-1", "-1"])
    assert capsys.readouterr().err == dedent(
        """\
        usage: PROG [-h] [-1 ONE] [foo]
        PROG: error: argument -1: expected one argument
        """
    )


# # specific tests


@pytest.mark.parametrize(
    "args, result",
    [
        (["-x", "2"], Namespace(foo=None, x=2)),
        (["-x", "-2"], Namespace(foo=None, x=-2)),
        (["5"], Namespace(foo="5", x=None)),
        pytest.param(
            ["-5"],
            Namespace(foo="-5", x=None),
            marks=pytest.mark.xfail(reason="possible feature"),
        ),
        pytest.param(
            ["-x", "hello"],
            Namespace(foo=None, x="hello"),
            marks=pytest.mark.xfail(reason="intended", raises=SystemExit),
        ),
    ],
)
def test_NegInt(args, result):
    parser = NegativeArgumentParser()
    parser.add_argument("foo", nargs="?")
    parser.add_argument("-x", type=NegInt)
    assert parser.parse_args(args) == result


@pytest.mark.parametrize(
    "args, result",
    [
        (["5"], Namespace(eggs=5.0)),
        (["-123.56"], Namespace(eggs=-123.56)),
        (["-1.34e-1"], Namespace(eggs=-0.134)),
    ],
)
def test_NegFloat(args, result):
    parser = NegativeArgumentParser()
    parser.add_argument("eggs", type=NegFloat)
    assert parser.parse_args(args) == result


@pytest.mark.parametrize(
    "args, result",
    [
        pytest.param(
            ["-ra", "14:29:43", "-dec", "-62:50:02"],
            Namespace(ra="14:29:43", dec="-62:50:02"),
            id="Proxima Cen",
        ),
        pytest.param(
            ["-ra", "17:57:49", "-dec", "+04:41:36"],
            Namespace(ra="17:57:49", dec="+04:41:36"),
            id="Barnard's Star",
        ),
    ],
)
def test_wcs(args, result):
    parser = NegativeArgumentParser()
    parser.add_argument("-ra", type=str)
    parser.add_argument("-dec", type=NegString)
    assert parser.parse_args(args) == result


@pytest.mark.xfail(reason="possible feature")
def test_pseudo_argument():
    parser = NegativeArgumentParser()
    parser.add_argument("x")
    assert parser.parse_args(["--", "-1"]) == Namespace(x="-1")


def test_pseudo_argument_revised():
    parser = NegativeArgumentParser()
    parser.add_argument("x", type=NegString)
    assert parser.parse_args(["--", "-1"]) == Namespace(x="-1")
