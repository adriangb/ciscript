import sys

if sys.version_info < (3, 9):
    from typing_extensions import Annotated, Literal
else:
    from typing import Annotated, Literal

if sys.version_info < (3, 8):
    from typing_extensions import Protocol, TypedDict
else:
    from typing import Protocol, TypedDict


__all__ = (
    "TypedDict",
    "Annotated",
    "Literal",
    "Protocol",
)
