from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar, Union

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True)
class Success(Generic[T]):
    data: T

    @property
    def is_success(self) -> bool:
        return True


@dataclass(frozen=True)
class Failure(Generic[E]):
    error: E

    @property
    def is_success(self) -> bool:
        return False


Result = Union[Success[T], Failure[E]]


def ok(data: T) -> Success[T]:
    return Success(data=data)


def fail(error: E) -> Failure[E]:
    return Failure(error=error)
