import json
from typing import IO

from pydantic import BaseModel
from yaml import SafeDumper, dump_all  # type: ignore


def export(model: BaseModel, file: IO[str]) -> None:
    data = json.loads(model.json(exclude_unset=True))
    dump_all([data], file, Dumper=SafeDumper, allow_unicode=True, sort_keys=False)
