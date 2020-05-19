"""Console script for onthefly."""
import sys
import click
from .onthefly import onthefly


@click.command()
@click.argument("input_file", default="/home/mroavi/Desktop/input.jl")
def main(input_file):
    """Emulates typing each character of an input file"""
    click.echo("Hey there!")
    onthefly(input_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
