from collections.abc import Callable
from typing import Protocol, TypeVar, overload

_T = TypeVar('_T')

class _PropertyFactory(Protocol):
    """The real callable factory returns its registered parser's value.

    This is the interface of the existing class object, not an instance type
    for the values it returns. A custom parser may return any Python object.
    """
    def __call__(self, buffer: bytes, prop_type: int) -> object: ...
    @overload
    def add_parser(self, prop_type: int, length: int | None = ..., func: None = ...) -> Callable[[Callable[[bytes], _T]], Callable[[bytes], _T]]: ...
    @overload
    def add_parser(self, prop_type: int, length: int | None = ..., *, func: Callable[[bytes], _T]) -> Callable[[bytes], _T]: ...
    @overload
    def add_parser(self, prop_type: int, length: int | None, func: Callable[[bytes], _T]) -> Callable[[bytes], _T]: ...

Property: _PropertyFactory
