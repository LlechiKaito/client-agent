from constants.line import LINE_MESSAGE_MAX_CHARS
from infrastructure.external.line.line_messaging_client import _split_message


def test_should_return_single_chunk_for_short_text() -> None:
    text = "短いメッセージ"
    result = _split_message(text)
    assert result == [text]


def test_should_return_single_chunk_at_exact_limit() -> None:
    text = "A" * LINE_MESSAGE_MAX_CHARS
    result = _split_message(text)
    assert result == [text]


def test_should_split_at_newline_boundary() -> None:
    line = "A" * 2000
    text = f"{line}\n{line}\n{line}\n{line}"
    result = _split_message(text)
    assert len(result) >= 2
    for chunk in result:
        assert len(chunk) <= LINE_MESSAGE_MAX_CHARS


def test_should_split_long_text_without_newlines() -> None:
    text = "B" * (LINE_MESSAGE_MAX_CHARS + 100)
    result = _split_message(text)
    assert len(result) == 2
    assert result[0] == "B" * LINE_MESSAGE_MAX_CHARS
    assert result[1] == "B" * 100


def test_should_handle_empty_text() -> None:
    result = _split_message("")
    assert result == [""]


def test_should_strip_leading_newlines_from_next_chunk() -> None:
    first_part = "A" * 4999
    text = f"{first_part}\n\n\nBBB"
    result = _split_message(text)
    assert len(result) == 2
    assert result[1] == "BBB"
