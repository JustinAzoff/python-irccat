from irccat import util

def test_extract_targets():
    cases = [
        ("hello world", ([], "hello world")),
        ("#log hello world", (["#log"], "hello world")),
        ("#log,@user hello world", (["#log","user"], "hello world")),
    ]
    for input, expected in cases:
        yield extract_case, input, expected

def extract_case(input, expected):
    out = util.extract_targets(input)

    assert out == expected
