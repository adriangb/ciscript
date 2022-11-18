from io import BytesIO, TextIOWrapper

from ciscript.github import Job, Step, Workflow
from ciscript.yaml import export
from tests.utils import Regressions


def test_basic(data_regression: Regressions) -> None:
    workflow = Workflow(
        on="push",
        jobs={
            "test": Job(
                name="test-ubuntu",
                runs_on="ubuntu-latest",
                steps=[Step(id="run pytest", run="pytest -v")],
            )
        },
    )

    file = TextIOWrapper(BytesIO())
    export(workflow, file)

    file.seek(0)

    got = file.read()
    data_regression.check(got)
