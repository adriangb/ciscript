from typing import Any, Protocol


class Regressions(Protocol):
    def check(self, data: Any) -> None:
        ...
