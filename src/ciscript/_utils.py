from __future__ import annotations

from typing import List


def dedent_escape_and_quote_aware(value: str) -> str:
    stack: List[str] = []
    splits: List[int] = []
    quotes = ("'", '"')
    escape = "\\"
    newline = "\n"
    for prev, (idx, char) in zip(value[1:], enumerate(value)):
        if char in quotes and prev != escape:
            if stack and stack[-1] == char:
                # closing
                stack.pop()
            else:
                stack.append(char)
        elif char == newline and not stack:
            splits.append(idx)
    if not splits:
        return value
    lines: List[str] = []
    prefix = len(value)
    for from_idx, to_idx in zip((-1, *splits), splits):
        line = value[from_idx + 1 : to_idx]
        idx = prefix
        for idx, c in enumerate(line):
            if c != " " or idx > prefix:
                break
        prefix = min(idx, prefix)
    for from_idx, to_idx in zip((-1, *splits), (*splits, len(value))):
        lines.append(value[from_idx + 1 : to_idx].removeprefix(prefix * " "))
    value = "\n".join(lines)
    return value
