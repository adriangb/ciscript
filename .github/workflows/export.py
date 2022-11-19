from pathlib import Path

from ciscript import github as gha
from ciscript.yaml import export

__all__ = ["workflow"]


OLDEST_PYTHON_MINOR_VERSION = 7
LATEST_PYTHON_MINOR_VERSION = 11


PYTHON_MATRIX_STRATEGY = gha.Strategy(
    matrix={
        "python": [
            f"3.{minor}"
            for minor in range(
                OLDEST_PYTHON_MINOR_VERSION, LATEST_PYTHON_MINOR_VERSION + 1
            )
        ]
    }
)


SETUP_POETRY = [
    gha.Step(uses="actions/checkout@v2"),
    gha.Step(
        name="Set up Python",
        uses="actions/setup-python@v2",
        with_={"python-version": "${{ matrix.python-version }}"},
    ),
    gha.Step(
        name="Install and configure Poetry",
        uses="snok/install-poetry@v1",
    ),
]
SETUP_PROJECT = [
    *SETUP_POETRY,
    gha.Step(name="Setup project", run="make init"),
]


workflow = gha.Workflow(
    name="CI/CD",
    on=gha.OnItems(pull_request={}, push=gha.PushEvent(branches=["main"])),
    defaults=gha.JobDefaults(run=gha.Run(shell="bash")),
    jobs={
        "lint": gha.Job(
            name="Run Linters",
            runs_on="ubuntu-latest",
            strategy=PYTHON_MATRIX_STRATEGY,
            steps=[
                *SETUP_PROJECT,
                gha.Step(name="Lint", run="make lint"),
            ],
        ),
        "test": gha.Job(
            name="Run Tests",
            runs_on="ubuntu-latest",
            strategy=PYTHON_MATRIX_STRATEGY,
            steps=[
                *SETUP_PROJECT,
                gha.Step(name="Test", run="make test"),
            ],
        ),
        "pypi": gha.Job(
            name="🚀 PyPi Release 📦",
            runs_on="ubuntu-latest",
            needs=["test", "lint"],
            strategy=PYTHON_MATRIX_STRATEGY,
            steps=[
                *SETUP_PROJECT,
                gha.Step(
                    name="PyPi release",
                    id="pypi",
                    run="""PACKAGE_VERSION=$(poetry version -s)
                    echo "package_version=$PACKAGE_VERSION" >> $GITHUB_ENV
                    printf "\nSee this release on GitHub: [v$PACKAGE_VERSION](https://github.com/$GITHUB_REPOSITORY/releases/tag/$PACKAGE_VERSION)\n" >> README.md
                    poetry config pypi-token.pypi "${{ secrets.PYPI_TOKEN }}"
                    poetry publish --build
                    """,
                ),
                gha.Step(
                    name="GitHub release",
                    uses="ncipollo/release-action@v1",
                    if_="steps.pypi.outcome == 'success'",
                    with_={
                        "token": "${{ secrets.GITHUB_TOKEN }}",
                        "tag": "${{ env.package_version }}",
                        "generateReleaseNotes": True,
                    },
                ),
            ],
        ),
    },
)


if __name__ == "__main__":
    with open(Path(__file__).parent / "workflow.yaml", mode="w") as f:
        export(workflow, f)
