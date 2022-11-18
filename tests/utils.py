from typing import Any

from ciscript._typing import Protocol


class Regressions(Protocol):
    def check(self, data: Any) -> None:
        ...
