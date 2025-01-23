#!/usr/bin/env python3

from typing import Annotated

from rich.console import Console
from typer import Argument, Typer

from fact.lib import factorial

app = Typer(add_completion=False)


@app.command()
def main(n: Annotated[int, Argument(min=0, help="The input n of fact(n)")]) -> None:
    """Compute the factorial of a given input.
    Args:
        n (int): The input number for which the factorial is to be computed. Must be a non-negative integer.
    """
    Console().print(f"fact({n}) = {factorial(n)}")


# Allow the script to be run standalone (useful during development).
if __name__ == "__main__":
    app()
