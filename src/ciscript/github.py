from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from pydantic import BaseConfig, BaseModel, Extra, Field, validator

from ciscript._typing import Annotated, Literal, TypedDict
from ciscript._utils import dedent_escape_and_quote_aware


class CustomBaseModel(BaseModel):
    class Config(BaseConfig):
        extra = Extra.forbid
        allow_population_by_field_name = True


class EmptyDict(TypedDict):
    """Helper type to allow on_push={} instead of on_push=OnPushEvent()"""


class Secrets(CustomBaseModel):
    description: Optional[str] = None
    """A string description of the secret parameter."""
    required: bool
    """A boolean specifying whether the secret must be supplied."""


class WorkflowCallEvent(CustomBaseModel):
    inputs: Optional[Dict[str, Inputs]] = None
    """When using the workflow_call keyword, you can optionally specify inputs that are passed to the called workflow from the caller workflow."""
    secrets: Optional[Dict[str, Secrets]] = None
    """A map of the secrets that can be used in the called workflow.
    Within the called workflow, you can use the secrets context to refer to a secret."""


class Inputs(CustomBaseModel):
    description: str
    """A string description of the input parameter."""
    deprecationMessage: Optional[str] = None
    """A string shown to users using the deprecated input."""
    required: Optional[bool] = None
    """A boolean to indicate whether the action requires the input parameter.
    Set to true when the parameter is required."""
    default: Optional[str] = None
    """A string representing the default value.
    The default value is used when an input parameter isn't specified in a workflow file."""
    type: Optional[Literal["string", "choice", "boolean", "environment"]] = None
    """A string representing the type of the input."""
    options: Optional[List[str]] = None
    """The options of the dropdown list, if the type is a choice."""

    @validator("options")
    def validate_options(
        cls, value: Optional[List[str]], values: Dict[str, Any]
    ) -> Optional[List[str]]:
        if values["type"] == "choice" and value is None:
            raise ValueError("options musr be specified for choices")
        elif values is not None:
            raise ValueError("options can only be specified for choice")


class WorkflowDispatch(CustomBaseModel):
    inputs: Optional[Dict[str, Inputs]] = None
    """Input parameters allow you to specify data that the action expects to use during runtime.
    GitHub stores input parameters as environment variables.
    Input ids with uppercase letters are converted to lowercase during runtime.
    We recommended using lowercase input ids."""


class ScheduleItem(CustomBaseModel):
    cron: Annotated[
        Optional[str],
        Field(
            regex="^(((\\d+,)+\\d+|((\\d+|\\*)/\\d+|((JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)(-(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC))?))|(\\d+-\\d+)|\\d+|\\*|((MON|TUE|WED|THU|FRI|SAT|SUN)(-(MON|TUE|WED|THU|FRI|SAT|SUN))?)) ?){5}$"
        ),
    ] = None


Architecture = Literal[
    "ARM32",
    "x64",
    "x86",
]


Configuration = Union[
    str, float, bool, Dict[str, "Configuration"], List["Configuration"]
]


class Credentials(CustomBaseModel):
    username: Optional[str] = None
    password: Optional[str] = None


Volume = Annotated[str, Field(regex="^[^:]+:[^:]+$")]


PermissionsLevel = Literal[
    "read",
    "write",
    "none",
]


class Environment(CustomBaseModel):

    name: str
    """The name of the environment configured in the repo."""
    url: Optional[str] = None
    """A deployment URL"""


Event = Literal[
    "branch_protection_rule",
    "check_run",
    "check_suite",
    "create",
    "delete",
    "deployment",
    "deployment_status",
    "discussion",
    "discussion_comment",
    "fork",
    "gollum",
    "issue_comment",
    "issues",
    "label",
    "member",
    "milestone",
    "page_build",
    "project",
    "project_card",
    "project_column",
    "public",
    "pull_request",
    "pull_request_review",
    "pull_request_review_comment",
    "pull_request_target",
    "push",
    "registry_package",
    "release",
    "status",
    "watch",
    "workflow_call",
    "workflow_dispatch",
    "workflow_run",
    "repository_dispatch",
]

EventObject = Union[Dict[str, Any], Any]


ExpressionSyntax = Annotated[str, Field(regex="^\\$\\{\\{(.|[\r\n])*\\}\\}$")]


StringContainingExpressionSyntax = Annotated[
    str, Field(regex="^.*\\$\\{\\{(.|[\r\n])*\\}\\}.*$")
]
"""An expression like ${{ matrix.version }}"""


Glob = Annotated[str, Field(min_length=1)]


Globs = Annotated[List[Glob], Field(min_items=1)]


Machine = Literal[
    "linux",
    "macos",
    "windows",
]


Name = Annotated[str, Field(regex="^[_a-zA-Z][a-zA-Z0-9_-]*$")]


Path = Globs


Shell = Literal["bash", "pwsh", "python", "sh", "cmd", "powershell"]
"""You can override the default shell settings in the runner's operating system using the shell keyword.
You can use built-in shell keywords, or you can define a custom set of shell options.
"""


Types = Annotated[
    List[str],
    Field(
        min_items=1,
    ),
]
"""Selects the types of activity that will trigger a workflow run.
Most GitHub events are triggered by more than one type of activity.
For example, the event for the release resource is triggered when a release is published, unpublished, created, edited, deleted, or prereleased.
The types keyword enables you to narrow down activity that causes the workflow to run.
When only one activity type triggers a webhook event, the types keyword is unnecessary.
You can use an array of event types.
For more information about each event and their activity types, see https://help.github.com/en/articles/events-that-trigger-workflows#webhook-events."""


WorkingDirectory = str
"""Using the working-directory keyword, you can specify the working directory of where to run the command."""


JobNeedArray = Annotated[List[Name], Field(min_items=1)]


JobNeeds = Union[JobNeedArray, Name]
"""Identifies any jobs that must complete successfully before this job will run.
It can be a string or array of strings.
If a job fails, all jobs that need it are skipped unless the jobs use a conditional statement that causes the job to continue."""


class Strategy(CustomBaseModel):
    matrix: Union[Dict[str, List[str]], ExpressionSyntax]
    """A build matrix is a set of different configurations of the virtual environment.
    For example you might run a job against more than one supported version of a language, operating system, or tool.
    Each configuration is a copy of the job that runs and reports a status.
    You can specify a matrix by supplying an array for the configuration options.
    For example, if the GitHub virtual environment supports Node.js versions 6, 8, and 10 you could specify an array of those versions in the matrix.
    When you define a matrix of operating systems, you must set the required runs-on keyword to the operating system of the current job, rather than hard-coding the operating system name.
    To access the operating system name, you can use the matrix.os context parameter to set runs-on.
    For more information, see https://help.github.com/en/articles/contexts-and-expression-syntax-for-github-actions."""
    fail_fast: Optional[bool] = True
    """When set to true, GitHub cancels all in-progress jobs if any matrix job fails.
    Default: true"""
    max_parallel: Optional[float] = None
    """The maximum number of jobs that can run simultaneously when using a matrix job strategy.
    By default, GitHub will maximize the number of jobs run in parallel depending on the available runners on GitHub-hosted virtual machines."""


Branch = Globs
"""When using the push and pull_request events, you can configure a workflow to run on specific branches or tags.
If you only define only tags or only branches, the workflow won't run for events affecting the undefined Git ref.
The branches, branches-ignore, tags, and tags-ignore keywords accept glob patterns that use the * and ** wildcard characters to match more than one branch or tag name.
For more information, see https://help.github.com/en/github/automating-your-workflow-with-github-actions/workflow-syntax-for-github-actions#filter-pattern-cheat-sheet.
The patterns defined in branches and tags are evaluated against the Git ref's name.
For example, defining the pattern mona/octocat in branches will match the refs/heads/mona/octocat Git ref.
The pattern releases/** will match the refs/heads/releases/10 Git ref.
You can use two types of filters to prevent a workflow from running on pushes and pull requests to tags and branches:\n- branches or branches-ignore - You cannot use both the branches and branches-ignore filters for the same event in a workflow.
Use the branches filter when you need to filter branches for positive matches and exclude branches.
Use the branches-ignore filter when you only need to exclude branch names.
- tags or tags-ignore - You cannot use both the tags and tags-ignore filters for the same event in a workflow.
Use the tags filter when you need to filter tags for positive matches and exclude tags.
Use the tags-ignore filter when you only need to exclude tag names.
You can exclude tags and branches using the ! character.
The order that you define patterns matters.
- A matching negative pattern (prefixed with !) after a positive match will exclude the Git ref.
- A matching positive pattern after a negative match will include the Git ref again."""


class Concurrency(CustomBaseModel):
    group: str
    """When a concurrent job or workflow is queued, if another job or workflow using the same concurrency group in the repository is in progress, the queued job or workflow will be pending.
    Any previously pending job or workflow in the concurrency group will be canceled."""
    cancel_in_progress: Annotated[
        Optional[Union[bool, ExpressionSyntax]],
        Field(
            alias="cancel-in-progress",
        ),
    ] = None
    """To cancel any currently running job or workflow in the same concurrency group, specify cancel-in-progress: true."""


class Run(CustomBaseModel):
    shell: Optional[Shell] = None
    working_directory: Annotated[
        Optional[WorkingDirectory], Field(alias="working-directory")
    ] = None


class JobDefaults(CustomBaseModel):
    run: Optional[Run] = None


class PermissionsEvent(CustomBaseModel):

    actions: Optional[PermissionsLevel] = None
    checks: Optional[PermissionsLevel] = None
    contents: Optional[PermissionsLevel] = None
    deployments: Optional[PermissionsLevel] = None
    discussions: Optional[PermissionsLevel] = None
    id_token: Annotated[Optional[PermissionsLevel], Field(alias="id-token")] = None
    issues: Optional[PermissionsLevel] = None
    packages: Optional[PermissionsLevel] = None
    pages: Optional[PermissionsLevel] = None
    pull_requests: Annotated[
        Optional[PermissionsLevel], Field(alias="pull-requests")
    ] = None
    repository_projects: Annotated[
        Optional[PermissionsLevel], Field(alias="repository-projects")
    ] = None
    security_events: Annotated[
        Optional[PermissionsLevel], Field(alias="security-events")
    ] = None
    statuses: Optional[PermissionsLevel] = None


Env = Union[Dict[str, Union[str, float, bool]], StringContainingExpressionSyntax]
"""To set custom environment variables, you need to specify the variables in the workflow file.
    You can define environment variables for a step, job, or entire workflow using the jobs.<job_id>.steps[*].env, jobs.<job_id>.env, and env keywords.
    For more information, see https://docs.github.com/en/actions/learn-github-actions/workflow-syntax-for-github-actions#jobsjob_idstepsenv"""


class Ref(CustomBaseModel):
    branches: Optional[Branch] = None
    branches_ignore: Annotated[Optional[Branch], Field(alias="branches-ignore")] = None
    tags: Optional[Branch] = None
    tags_ignore: Annotated[Optional[Branch], Field(alias="tags-ignore")] = None
    paths: Optional[Path] = None
    """Use the paths-ignore filter when you only need to exclude path names."""
    paths_ignore: Annotated[Optional[Path], Field(alias="paths-ignore")] = None
    """Use the paths filter when you need to filter paths for positive matches and exclude paths."""


class ReusableWorkflowCallJob(CustomBaseModel):

    name: Optional[str] = None
    """The name of the job displayed on GitHub."""
    needs: Optional[JobNeeds] = None
    permissions: Optional[PermissionsEvent] = None
    if_: Annotated[
        Optional[Union[bool, float, str]],
        Field(
            alias="if",
        ),
    ] = None
    """You can use the if conditional to prevent a job from running unless a condition is met.
    You can use any supported context and expression to create a conditional.
    Expressions in an if conditional do not require the ${{ }} syntax.
    For more information, see https://help.github.com/en/articles/contexts-and-expression-syntax-for-github-actions."""
    uses: Annotated[
        str,
        Field(
            regex="^(.+/)+(.+)\\.(ya?ml)(@.+)?$",
        ),
    ]
    """The location and version of a reusable workflow file to run as a job, of the form './{path/to}/{localfile}.yml' or '{owner}/{repo}/{path}/{filename}@{ref}'.
    {ref} can be a SHA, a release tag, or a branch name.
    Using the commit SHA is the safest for stability and security"""
    with_: Annotated[
        Optional[Env],
        Field(
            alias="with",
        ),
    ] = None
    """A map of inputs that are passed to the called workflow.
    Any inputs that you pass must match the input specifications defined in the called workflow.
    Unlike 'jobs.<job_id>.steps[*].with', the inputs you pass with 'jobs.<job_id>.with' are not be available as environment variables in the called workflow.
    Instead, you can reference the inputs by using the inputs context."""
    secrets: Optional[Union[Env, Literal["inherit"]]] = None
    """When a job is used to call a reusable workflow, you can use 'secrets' to provide a map of secrets that are passed to the called workflow.
    Any secrets that you pass must match the names defined in the called workflow."""
    strategy: Optional[Strategy] = None
    """A strategy creates a build matrix for your jobs.
    You can define different variations of an environment to run each job in."""
    concurrency: Optional[Union[str, Concurrency]] = None
    """Concurrency ensures that only a single job or workflow using the same concurrency group will run at a time.
    A concurrency group can be any string or expression.
    The expression can use any context except for the secrets context.
    You can also specify concurrency at the workflow level.
    When a concurrent job or workflow is queued, if another job or workflow using the same concurrency group in the repository is in progress, the queued job or workflow will be pending.
    Any previously pending job or workflow in the concurrency group will be canceled.
    To also cancel any currently running job or workflow in the same concurrency group, specify cancel-in-progress: true."""


class Step(CustomBaseModel):
    """A job contains a sequence of tasks called steps. Steps can run commands,
    run setup tasks, or run an action in your repository, a public repository,
    or an action published in a Docker registry. Not all steps run actions, but
    all actions run as a step. Each step runs in its own process in the runner
    environment and has access to the workspace and filesystem. Because steps
    run in their own process, changes to environment variables are not
    preserved between steps. GitHub provides built-in steps to set up and
    complete a job.

    See https://help.github.com/en/actions/automating-your-workflow-with-github-actions/workflow-syntax-for-github-actions#jobsjob_idsteps

    """

    id: Optional[str] = None
    """"A unique identifier for the step.
    You can use the id to reference the step in contexts.
    For more information, see https://help.github.com/en/articles/contexts-and-expression-syntax-for-github-actions."""
    if_: Annotated[
        Optional[Union[bool, float, str]],
        Field(
            alias="if",
        ),
    ] = None
    """You can use the if conditional to prevent a step from running unless a condition is met.
    You can use any supported context and expression to create a conditional.
    Expressions in an if conditional do not require the ${{ }} syntax.
    For more information, see https://help.github.com/en/articles/contexts-and-expression-syntax-for-github-actions."""
    name: Optional[str] = None
    """A name for your step to display on GitHub."""
    uses: Optional[str] = None
    """Selects an action to run as part of a step in your job.
    An action is a reusable unit of code.
    You can use an action defined in the same repository as the workflow, a public repository, or in a published Docker container image (https://hub.docker.com/).
    We strongly recommend that you include the version of the action you are using by specifying a Git ref, SHA, or Docker tag number.
    If you don't specify a version, it could break your workflows or cause unexpected behavior when the action owner publishes an update.
    - Using the commit SHA of a released action version is the safest for stability and security.
    - Using the specific major action version allows you to receive critical fixes and security patches while still maintaining compatibility.
    It also assures that your workflow should still work.
    - Using the master branch of an action may be convenient, but if someone releases a new major version with a breaking change, your workflow could break.
    Some actions require inputs that you must set using the with keyword.
    Review the action's README file to determine the inputs required.
    Actions are either JavaScript files or Docker containers.
    If the action you're using is a Docker container you must run the job in a Linux virtual environment.
    For more details, see https://help.github.com/en/articles/virtual-environments-for-github-actions."""
    run: Optional[str] = None
    """Runs command-line programs using the operating system's shell.
    If you do not provide a name, the step name will default to the text specified in the run command.
    Commands run using non-login shells by default.
    You can choose a different shell and customize the shell used to run commands.
    For more information, see https://help.github.com/en/actions/automating-your-workflow-with-github-actions/workflow-syntax-for-github-actions#using-a-specific-shell.
    Each run keyword represents a new process and shell in the virtual environment.
    When you provide multi-line commands, each line runs in the same shell."""
    working_directory: Annotated[
        Optional[WorkingDirectory], Field(alias="working-directory")
    ] = None
    shell: Optional[Shell] = None
    with_: Annotated[
        Optional[Env],
        Field(
            alias="with",
        ),
    ] = None
    """A map of the input parameters defined by the action.
    Each input parameter is a key/value pair.
    Input parameters are set as environment variables.
    The variable is prefixed with INPUT_ and converted to upper case."""
    env: Optional[Env] = None
    """Sets environment variables for steps to use in the virtual environment.
    You can also set environment variables for the entire workflow or a job."""
    continue_on_error: Annotated[
        Optional[Union[bool, ExpressionSyntax]],
        Field(
            alias="continue-on-error",
        ),
    ] = False
    """Prevents a job from failing when a step fails.
    Set to true to allow a job to pass when this step fails."""
    timeout_minutes: Annotated[
        Optional[float],
        Field(
            alias="timeout-minutes",
        ),
    ] = None
    """The maximum number of minutes to run the step before killing the process."""

    @validator("run")
    def cleanup_multiline_run(cls, value: str) -> str:
        return dedent_escape_and_quote_aware(value)


class BranchProtectionRuleEvent(CustomBaseModel):
    types: Optional[List[Literal["created", "edited", "deleted"]]] = None


class CheckRunEvent(CustomBaseModel):
    types: Optional[
        List[Literal["created", "requested", "completed", "requested_action"]]
    ] = None


class CheckSuiteEvent(CustomBaseModel):
    types: Optional[List[Literal["completed"]]] = None


PullRequestEventType = Literal[
    "assigned",
    "unassigned",
    "labeled",
    "unlabeled",
    "opened",
    "edited",
    "closed",
    "reopened",
    "synchronize",
    "converted_to_draft",
    "ready_for_review",
    "locked",
    "unlocked",
    "review_requested",
    "review_request_removed",
    "auto_merge_enabled",
    "auto_merge_disabled",
]


class PullRequestEvent(CustomBaseModel):
    types: Optional[List[PullRequestEventType]] = None


PushEventTypes = Literal[
    "assigned",
    "unassigned",
    "labeled",
    "unlabeled",
    "opened",
    "edited",
    "closed",
    "reopened",
    "synchronize",
    "converted_to_draft",
    "ready_for_review",
    "locked",
    "unlocked",
    "review_requested",
    "review_request_removed",
    "auto_merge_enabled",
    "auto_merge_disabled",
]


class PushEvent(CustomBaseModel):
    types: Optional[List[PushEventTypes]] = None
    branches: Optional[List[Glob]] = None


class OnItems(CustomBaseModel):
    branch_protection_rule: Optional[Union[BranchProtectionRuleEvent, EmptyDict]] = None
    """Runs your workflow anytime the branch_protection_rule event occurs.
    More than one activity type triggers this event."""
    check_run: Optional[CheckRunEvent] = None
    """Runs your workflow anytime the check_run event occurs.
    More than one activity type triggers this event.
    For information about the REST API, see https://developer.github.com/v3/checks/runs."""
    check_suite: Optional[CheckSuiteEvent] = None
    """Runs your workflow anytime the check_suite event occurs.
    More than one activity type triggers this event.
    For information about the REST API, see https://developer.github.com/v3/checks/suites/."""
    create: Optional[EventObject] = None
    """Runs your workflow anytime someone creates a branch or tag, which triggers the create event.
    For information about the REST API, see https://developer.github.com/v3/git/refs/#create-a-reference."""
    delete: Optional[EventObject] = None
    """Runs your workflow anytime someone deletes a branch or tag, which triggers the delete event.
    For information about the REST API, see https://developer.github.com/v3/git/refs/#delete-a-reference."""
    deployment: Optional[EventObject] = None
    """Runs your workflow anytime someone creates a deployment, which triggers the deployment event.
    Deployments created with a commit SHA may not have a Git ref.
    For information about the REST API, see https://developer.github.com/v3/repos/deployments/."""
    deployment_status: Optional[EventObject] = None
    """Runs your workflow anytime a third party provides a deployment status, which triggers the deployment_status event.
    Deployments created with a commit SHA may not have a Git ref.
    For information about the REST API, see https://developer.github.com/v3/repos/deployments/#create-a-deployment-status."""
    discussion: Optional[EventObject] = None
    """Runs your workflow anytime the discussion event occurs.
    More than one activity type triggers this event.
    For information about the GraphQL API, see https://docs.github.com/en/graphql/guides/using-the-graphql-api-for-discussions"""
    discussion_comment: Optional[EventObject] = None
    """Runs your workflow anytime the discussion_comment event occurs.
    More than one activity type triggers this event.
    For information about the GraphQL API, see https://docs.github.com/en/graphql/guides/using-the-graphql-api-for-discussions"""
    fork: Optional[EventObject] = None
    """Runs your workflow anytime when someone forks a repository, which triggers the fork event.
    For information about the REST API, see https://developer.github.com/v3/repos/forks/#create-a-fork."""
    gollum: Optional[EventObject] = None
    """Runs your workflow when someone creates or updates a Wiki page, which triggers the gollum event."""
    issue_comment: Optional[EventObject] = None
    """Runs your workflow anytime the issue_comment event occurs.
    More than one activity type triggers this event.
    For information about the REST API, see https://developer.github.com/v3/issues/comments/."""
    issues: Optional[EventObject] = None
    """Runs your workflow anytime the issues event occurs.
    More than one activity type triggers this event.
    For information about the REST API, see https://developer.github.com/v3/issues."""
    label: Optional[EventObject] = None
    """Runs your workflow anytime the label event occurs.
    More than one activity type triggers this event.
    For information about the REST API, see https://developer.github.com/v3/issues/labels/."""
    member: Optional[EventObject] = None
    """Runs your workflow anytime the member event occurs.
    More than one activity type triggers this event.
    For information about the REST API, see https://developer.github.com/v3/repos/collaborators/."""
    merge_group: Optional[EventObject] = None
    """Runs your workflow when a pull request is added to a merge queue, which adds the pull request to a merge group.
    For information about the merge queue, see https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/merging-a-pull-request-with-a-merge-queue ."""
    milestone: Optional[EventObject] = None
    """Runs your workflow anytime the milestone event occurs.
    More than one activity type triggers this event.
    For information about the REST API, see https://developer.github.com/v3/issues/milestones/."""
    page_build: Optional[EventObject] = None
    """Runs your workflow anytime someone pushes to a GitHub Pages-enabled branch, which triggers the page_build event.
    For information about the REST API, see https://developer.github.com/v3/repos/pages/."""
    project: Optional[EventObject] = None
    """Runs your workflow anytime the project event occurs.
    More than one activity type triggers this event.
    For information about the REST API, see https://developer.github.com/v3/projects/."""
    project_card: Optional[EventObject] = None
    """Runs your workflow anytime the project_card event occurs.
    More than one activity type triggers this event.
    For information about the REST API, see https://developer.github.com/v3/projects/cards."""
    project_column: Optional[EventObject] = None
    """Runs your workflow anytime the project_column event occurs.
    More than one activity type triggers this event.
    For information about the REST API, see https://developer.github.com/v3/projects/columns."""
    public: Optional[EventObject] = None
    """Runs your workflow anytime someone makes a private repository public, which triggers the public event.
    For information about the REST API, see https://developer.github.com/v3/repos/#edit."""
    pull_request: Optional[Union[PullRequestEvent, EmptyDict]] = None
    """Runs your workflow anytime the pull_request event occurs.
    More than one activity type triggers this event.
    For information about the REST API, see https://developer.github.com/v3/pulls.
    Note: Workflows do not run on private base repositories when you open a pull request from a forked repository.
    When you create a pull request from a forked repository to the base repository, GitHub sends the pull_request event to the base repository and no pull request events occur on the forked repository.
    Workflows don't run on forked repositories by default.
    You must enable GitHub Actions in the Actions tab of the forked repository.
    The permissions for the GITHUB_TOKEN in forked repositories is read-only.
    For more information about the GITHUB_TOKEN, see https://help.github.com/en/articles/virtual-environments-for-github-actions."""
    pull_request_review: Optional[EventObject] = None
    """Runs your workflow anytime the pull_request_review event occurs.
    More than one activity type triggers this event.
    For information about the REST API, see https://developer.github.com/v3/pulls/reviews.
    Note: Workflows do not run on private base repositories when you open a pull request from a forked repository.
    When you create a pull request from a forked repository to the base repository, GitHub sends the pull_request event to the base repository and no pull request events occur on the forked repository.
    Workflows don't run on forked repositories by default.
    You must enable GitHub Actions in the Actions tab of the forked repository.
    The permissions for the GITHUB_TOKEN in forked repositories is read-only.
    For more information about the GITHUB_TOKEN, see https://help.github.com/en/articles/virtual-environments-for-github-actions."""
    pull_request_review_comment: Optional[EventObject] = None
    """Runs your workflow anytime a comment on a pull request's unified diff is modified, which triggers the pull_request_review_comment event.
    More than one activity type triggers this event.
    For information about the REST API, see https://developer.github.com/v3/pulls/comments.
    Note: Workflows do not run on private base repositories when you open a pull request from a forked repository.
    When you create a pull request from a forked repository to the base repository, GitHub sends the pull_request event to the base repository and no pull request events occur on the forked repository.
    Workflows don't run on forked repositories by default.
    You must enable GitHub Actions in the Actions tab of the forked repository.
    The permissions for the GITHUB_TOKEN in forked repositories is read-only.
    For more information about the GITHUB_TOKEN, see https://help.github.com/en/articles/virtual-environments-for-github-actions."""
    pull_request_target: Optional[None] = None
    """This event is similar to pull_request, except that it runs in the context of the base repository of the pull request, rather than in the merge commit.
    This means that you can more safely make your secrets available to the workflows triggered by the pull request, because only workflows defined in the commit on the base repository are run.
    For example, this event allows you to create workflows that label and comment on pull requests, based on the contents of the event payload."""
    push: Optional[Union[PushEvent, EmptyDict]] = None
    """Runs your workflow when someone pushes to a repository branch, which triggers the push event.
    Note: The webhook payload available to GitHub Actions does not include the added, removed, and modified attributes in the commit object.
    You can retrieve the full commit object using the REST API.
    For more information, see https://developer.github.com/v3/repos/commits/#get-a-single-commit."""
    registry_package: Optional[EventObject] = None
    """Runs your workflow anytime a package is published or updated.
    For more information, see https://help.github.com/en/github/managing-packages-with-github-packages."""
    release: Optional[EventObject] = None
    """Runs your workflow anytime the release event occurs.
    More than one activity type triggers this event.
    For information about the REST API, see https://developer.github.com/v3/repos/releases/ in the GitHub Developer documentation."""
    status: Optional[EventObject] = None
    """Runs your workflow anytime the status of a Git commit changes, which triggers the status event.
    For information about the REST API, see https://developer.github.com/v3/repos/statuses/."""
    watch: Optional[EventObject] = None
    """Runs your workflow anytime the watch event occurs.
    More than one activity type triggers this event.
    For information about the REST API, see https://developer.github.com/v3/activity/starring/."""
    workflow_call: Optional[WorkflowCallEvent] = None
    """"Allows workflows to be reused by other workflows."""
    workflow_dispatch: Optional[WorkflowDispatch] = None
    """You can now create workflows that are manually triggered with the new workflow_dispatch event.
    You will then see a 'Run workflow' button on the Actions tab, enabling you to easily trigger a run."""
    workflow_run: Optional[EventObject] = None
    """This event occurs when a workflow run is requested or completed, and allows you to execute a workflow based on the finished result of another workflow.
    For example, if your pull_request workflow generates build artifacts, you can create a new workflow that uses workflow_run to analyze the results and add a comment to the original pull request."""
    repository_dispatch: Optional[EventObject] = None
    """You can use the GitHub API to trigger a webhook event called repository_dispatch when you want to trigger a workflow for activity that happens outside of GitHub.
    For more information, see https://developer.github.com/v3/repos/#create-a-repository-dispatch-event.
    To trigger the custom repository_dispatch webhook event, you must send a POST request to a GitHub API endpoint and provide an event_type name to describe the activity type.
    To trigger a workflow run, you must also configure your workflow to use the repository_dispatch event."""
    schedule: Annotated[
        Optional[List[ScheduleItem]],
        Field(
            min_items=1,
        ),
    ] = None
    """You can schedule a workflow to run at specific UTC times using POSIX cron syntax (https://pubs.opengroup.org/onlinepubs/9699919799/utilities/crontab.html#tag_20_25_07).
    Scheduled workflows run on the latest commit on the default or base branch.
    The shortest interval you can run scheduled workflows is once every 5 minutes.
    Note: GitHub Actions does not support the non-standard syntax @yearly, @monthly, @weekly, @daily, @hourly, and @reboot.
    You can use crontab guru (https://crontab.guru/).
    to help generate your cron syntax and confirm what time it will run.
    To help you get started, there is also a list of crontab guru examples (https://crontab.guru/examples.html)."""


class Container(CustomBaseModel):

    image: str
    """The Docker image to use as the container to run the action.
    The value can be the Docker Hub image name or a registry name."""
    credentials: Optional[Credentials] = None
    """If the image's container registry requires authentication to pull the image, you can use credentials to set a map of the username and password.
    The credentials are the same values that you would provide to the `docker login` command."""
    env: Optional[Env] = None
    """Sets an array of environment variables in the container."""
    ports: Annotated[
        Optional[List[Union[float, str]]],
        Field(
            min_items=1,
        ),
    ] = None
    """Sets an array of ports to expose on the container."""
    volumes: Annotated[
        Optional[List[Volume]],
        Field(
            min_items=1,
        ),
    ] = None
    """Sets an array of volumes for the container to use.
    You can use volumes to share data between services or other steps in a job.
    You can specify named Docker volumes, anonymous Docker volumes, or bind mounts on the host.
    To specify a volume, you specify the source and destination path: <source>:<destinationPath>\nThe <source> is a volume name or an absolute path on the host machine, and <destinationPath> is an absolute path in the container."""
    options: Optional[str] = None
    """Additional Docker container resource options.
    For a list of options, see https://docs.docker.com/engine/reference/commandline/create/#options."""


Permissions = Union[Literal["read-all", "write-all"], PermissionsEvent]
"""You can modify the default permissions granted to the GITHUB_TOKEN, adding or removing access as required, so that you only allow the minimum required access."""


RunnerPlatform = Literal[
    "macos-10.15",
    "macos-11",
    "macos-12",
    "macos-latest",
    "self-hosted",
    "ubuntu-18.04",
    "ubuntu-20.04",
    "ubuntu-22.04",
    "ubuntu-latest",
    "windows-2019",
    "windows-2022",
    "windows-latest",
]


class Job(CustomBaseModel):
    """A workflow run is made up of one or more jobs, which run in parallel by
    default. To run jobs sequentially, you can define dependencies on other
    jobs using the jobs.<job_id>.needs keyword.

    Each job runs in a runner environment specified by runs-on.

    You can run an unlimited number of jobs as long as you are within the workflow usage limits.
    For more information, see "Usage limits and billing" for GitHub-hosted runners and "About self-hosted runners" for self-hosted runner usage limits.

    If you need to find the unique identifier of a job running in a workflow run, you can use the GitHub API.
    For more information, see "Workflow Jobs."

    See https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#jobs

    """

    name: Optional[str] = None
    """The name of the job displayed on GitHub."""
    needs: Optional[JobNeeds] = None
    permissions: Optional[Permissions] = None
    runs_on: Annotated[
        Union[
            RunnerPlatform,
            List[RunnerPlatform],
            StringContainingExpressionSyntax,
        ],
        Field(
            alias="runs-on",
        ),
    ]
    """The type of machine to run the job on.
    The machine can be either a GitHub-hosted runner, or a self-hosted runner."""
    environment: Optional[Union[str, Environment]] = None
    """The environment that the job references."""
    outputs: Optional[Dict[str, str]] = None
    """A map of outputs for a job.
    Job outputs are available to all downstream jobs that depend on this job."""
    env: Optional[Env] = None
    """A map of environment variables that are available to all steps in the job."""
    defaults: Optional[JobDefaults] = None
    """A map of default settings that will apply to all steps in the job."""
    if_: Annotated[
        Optional[Union[bool, float, str]],
        Field(
            alias="if",
        ),
    ] = None
    """You can use the if conditional to prevent a job from running unless a condition is met.
    You can use any supported context and expression to create a conditional.
    Expressions in an if conditional do not require the ${{ }} syntax.
    For more information, see https://help.github.com/en/articles/contexts-and-expression-syntax-for-github-actions."""
    steps: Annotated[
        Optional[List[Step]],
        Field(
            min_items=1,
        ),
    ] = None
    """"A job contains a sequence of tasks called steps.
    Steps can run commands, run setup tasks, or run an action in your repository, a public repository, or an action published in a Docker registry.
    Not all steps run actions, but all actions run as a step.
    Each step runs in its own process in the virtual environment and has access to the workspace and filesystem.
    Because steps run in their own process, changes to environment variables are not preserved between steps.
    GitHub provides built-in steps to set up and complete a job.
    Must contain either `uses` or `run`"""
    timeout_minutes: Optional[float] = 360
    """The maximum number of minutes to let a workflow run before GitHub automatically cancels it.
    Default: 360"""
    strategy: Optional[Strategy] = None
    """A strategy creates a build matrix for your jobs.
    You can define different variations of an environment to run each job in."""
    continue_on_error: Annotated[
        Optional[Union[bool, ExpressionSyntax]],
        Field(
            alias="continue-on-error",
        ),
    ] = None
    """Prevents a workflow run from failing when a job fails.
    Set to true to allow a workflow run to pass when this job fails."""
    container: Optional[Union[str, Container]] = None
    """A container to run any steps in a job that don't already specify a container.
    If you have steps that use both script and container actions, the container actions will run as sibling containers on the same network with the same volume mounts.
    If you do not set a container, all steps will run directly on the host specified by runs-on unless a step refers to an action configured to run in a container."""
    services: Optional[Dict[str, Container]] = None
    """Additional containers to host services for a job in a workflow.
    These are useful for creating databases or cache services like redis.
    The runner on the virtual machine will automatically create a network and manage the life cycle of the service containers.
    When you use a service container for a job or your step uses container actions, you don't need to set port information to access the service.
    Docker automatically exposes all ports between containers on the same network.
    When both the job and the action run in a container, you can directly reference the container by its hostname.
    The hostname is automatically mapped to the service name.
    When a step does not use a container action, you must access the service using localhost and bind the ports."""
    concurrency: Optional[Union[str, Concurrency]] = None
    """Concurrency ensures that only a single job or workflow using the same concurrency group will run at a time.
    A concurrency group can be any string or expression.
    The expression can use any context except for the secrets context.
    You can also specify concurrency at the workflow level.
    When a concurrent job or workflow is queued, if another job or workflow using the same concurrency group in the repository is in progress, the queued job or workflow will be pending.
    Any previously pending job or workflow in the concurrency group will be canceled.
    To also cancel any currently running job or workflow in the same concurrency group, specify cancel-in-progress: true."""


class Workflow(CustomBaseModel):
    name: Optional[str] = None
    """The name of your workflow.
    GitHub displays the names of your workflows on your repository's actions page.
    If you omit this field, GitHub sets the name to the workflow's filename."""
    on: Union[Event, List[Event], OnItems]
    """The name of the GitHub event that triggers the workflow.
    You can provide a single event string, array of events, array of event types, or an event configuration map that schedules a workflow or restricts the execution of a workflow to specific files, tags, or branch changes.
    For a list of available events, see https://help.github.com/en/github/automating-your-workflow-with-github-actions/events-that-trigger-workflows."""
    env: Optional[Env] = None
    """A map of environment variables that are available to all jobs and steps in the workflow."""
    defaults: Optional[JobDefaults] = None
    """A map of default settings that will apply to all jobs in the workflow."""
    concurrency: Optional[Union[str, Concurrency]] = None
    """Concurrency ensures that only a single job or workflow using the same concurrency group will run at a time.
    A concurrency group can be any string or expression.
    The expression can use any context except for the secrets context.
    You can also specify concurrency at the workflow level.
    When a concurrent job or workflow is queued, if another job or workflow using the same concurrency group in the repository is in progress, the queued job or workflow will be pending.
    Any previously pending job or workflow in the concurrency group will be canceled.
    To also cancel any currently running job or workflow in the same concurrency group, specify cancel-in-progress: true."""
    jobs: Dict[str, Union[Job, ReusableWorkflowCallJob]]
    """A workflow run is made up of one or more jobs.
    Jobs run in parallel by default.
    To run jobs sequentially, you can define dependencies on other jobs using the jobs.<job_id>.needs keyword.
    Each job runs in a fresh instance of the virtual environment specified by runs-on.
    You can run an unlimited number of jobs as long as you are within the workflow usage limits.
    For more information, see https://help.github.com/en/github/automating-your-workflow-with-github-actions/workflow-syntax-for-github-actions#usage-limits."""
    run_name: Annotated[
        Optional[str],
        Field(
            alias="run-name",
        ),
    ] = None
    """The name for workflow runs generated from the workflow.
    GitHub displays the workflow run name in the list of workflow runs on your repository's 'Actions' tab."""
    permissions: Optional[Permissions] = None
