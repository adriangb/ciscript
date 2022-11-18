from pathlib import Path

from ciscript.github import Job, OnItems, PushEvent, Step, Strategy, Workflow
from ciscript.yaml import export

OLDEST_PYTHON_MINOR_VERSION = 7
LATEST_PYTHON_MINOR_VERSION = 11


workflow = Workflow(
    name="CI/CD",
    on=OnItems(pull_request={}, push=PushEvent(branches=["main"])),
    jobs={
        "lint": Job(
            name="Run Linters",
            runs_on="ubuntu-latest",
            strategy=Strategy(
                matrix={
                    "python": [
                        f"3.{minor}"
                        for minor in range(
                            OLDEST_PYTHON_MINOR_VERSION, LATEST_PYTHON_MINOR_VERSION
                        )
                    ]
                }
            ),
            steps=[
                Step(uses="actions/checkout@v2"),
                Step(
                    name="Set up Python",
                    uses="actions/setup-python@v2",
                    with_={"python-version": "${{ matrix.python-version }}"},
                ),
                Step(
                    name="Install and configure Poetry",
                    uses="snok/intall-poetry@v1.3.1",
                ),
                Step(name="Lint", run="make lint"),
            ],
        )
    },
)


if __name__ == "__main__":
    with open(Path(__file__).parent / "workflow.yaml", mode="w") as f:
        export(workflow, f)
