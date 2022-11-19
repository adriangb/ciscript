from io import BytesIO, TextIOWrapper

from ciscript.github import Job, Step, Workflow
from ciscript.yaml import export
from tests.utils import Regressions


def test_basic(file_regression: Regressions) -> None:
    workflow = Workflow(
        on="push",
        jobs={
            "test": Job(
                name="test-ubuntu",
                runs_on="ubuntu-latest",
                steps=[
                    Step(
                        id="run pytest",
                        # check how we manipulate multiline strings with
                        # quotes and escaping
                        run="""\
                        apt-get install -y build-essential && \\
                            pytest -v
                        echo "\\"\n'\n'"
                        """,
                    )
                ],
            )
        },
    )

    file = TextIOWrapper(BytesIO())
    export(workflow, file)

    file.seek(0)

    got = file.read()
    file_regression.check(got)
