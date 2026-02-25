from domain.commons.result import Failure, Success, fail, ok


def test_ok_returns_success() -> None:
    result = ok("hello")
    assert isinstance(result, Success)
    assert result.is_success is True
    assert result.data == "hello"


def test_fail_returns_failure() -> None:
    result = fail("something went wrong")
    assert isinstance(result, Failure)
    assert result.is_success is False
    assert result.error == "something went wrong"
