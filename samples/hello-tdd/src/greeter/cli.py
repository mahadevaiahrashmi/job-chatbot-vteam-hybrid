# agent-notes: { ctx: "Click CLI entry point for greeter", deps: ["tests/test_greet.py"], state: active, last: "sato@2026-03-15" }

"""Greeter CLI -- a simple greeting tool.

Written by Sato (green phase) to make Tara's tests pass.
"""

import click


def greet(name: str = "World") -> str:
    """Return a greeting for the given name.

    Args:
        name: Who to greet. Defaults to "World".

    Returns:
        The greeting string.

    Raises:
        ValueError: If name is an empty string.
    """
    if name == "":
        raise ValueError("Name cannot be empty")
    return f"Hello, {name}!"


@click.group()
def cli():
    """A simple greeting tool."""


@cli.command()
@click.option("--name", default="World", help="Who to greet.")
def hello(name: str):
    """Print a greeting."""
    click.echo(greet(name))
