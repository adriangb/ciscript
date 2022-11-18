from io import BytesIO, TextIOWrapper

from ciscript.github import Job, Step, Workflow
from ciscript.yaml import export


def test_basic() -> None:
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

    expected = """\
    jobs:
      test:
        name: test-ubuntu
        runs_on: ubuntu-latest
        steps:
        - id: run pytest
          run: pytest -v
    'on': push
    """
    assert file.read() == expected
