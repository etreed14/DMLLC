import dmllc.format_transcript as ft


def test_parse_seconds():
    assert ft.parse_seconds('1.5s') == 1.5
    assert ft.parse_seconds('0s') == 0.0


def test_format_transcript_basic():
    words = [
        {'word': 'Hello', 'startTime': '0s', 'speakerTag': 1},
        {'word': 'world', 'startTime': '0.5s', 'speakerTag': 1},
        {'word': 'Hi', 'startTime': '60s', 'speakerTag': 2},
    ]
    result = ft.format_transcript(words)
    assert 'S1|0 Hello world' in result
    assert 'S2|1 Hi' in result
