import sys

# pydantic requires TypedDict to come from typing-extensions for Python < 3.9.2
if sys.version_info < (3, 10):
    from typing_extensions import TypedDict
else:
    from typing import TypedDict

if sys.version_info < (3, 9):
    from typing_extensions import Annotated, Literal
else:
    from typing import Annotated, Literal

if sys.version_info < (3, 8):
    from typing_extensions import Protocol
else:
    from typing import Protocol


__all__ = (
    "TypedDict",
    "Annotated",
    "Literal",
    "Protocol",
)
