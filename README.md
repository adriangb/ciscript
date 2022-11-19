# ciscript

Do you have a super complex CI workflow? Are you using YAML hooks or `!reference` in GitLab? Are you tired of pushing to CI just to find out that thing was supposed to be a list and not a map? Did you get bit by using `3.10` as your Python version and getting that converted to `3.1` because YAML? Do you wish you could just write some simple mostly declerative code instead? Well, here you go!

## How to use this

You create a source code file (currently only Python) and then export that to a YAML file that your CI system understands. This file should be commited to your repo so that there is nothing happening at "runtime". In other words, this is basically just a templating system with type checking and autocompletion.

### Example

This repo dogfoods itself. The way I set it up here is:

- [.github/workflows/export.py](.github/workflows/export.py) contains the workflow definition.
- [.pre-commit-config.yaml](].pre-commit-config.yaml) runs [.github/workflows/export.py](.github/workflows/export.py) on every commit to make sure [.github/workflows/workflow.yaml](.github/workflows/workflow.yaml) is laways up to date and you don't have to remember to run anything if you change the workflow.

That's it!

## Future

This is just an experiment for now.
I think it would be really interesting to write in TypeScript, that's probably the best language for boilerplate free declarative templating like this.
