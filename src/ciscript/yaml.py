import json
from typing import IO, Any

from pydantic import BaseModel
from yaml import Dumper, SafeDumper, dump_all  # type: ignore


def str_presenter(dumper: Dumper, data: str) -> Any:
    """configures yaml for dumping multiline strings
    Ref: https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data"""
    data = data.rstrip()
    if data.count("\n") > 0:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")  # type: ignore
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)  # type: ignore


def export(model: BaseModel, file: IO[str]) -> None:
    data = json.loads(model.json(exclude_unset=True, by_alias=True))
    SafeDumper.add_representer(str, str_presenter)  # type: ignore
    dump_all(
        [data], file, Dumper=SafeDumper, allow_unicode=True, sort_keys=False, width=2048
    )
