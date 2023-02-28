from typing import Callable, TypeVar, List

T1 = TypeVar("T1")
T2 = TypeVar("T2")


def list_map(f: Callable[[T1], T2], iterable: List[T1]) -> List[T2]:
    return list(map(f, iterable))
