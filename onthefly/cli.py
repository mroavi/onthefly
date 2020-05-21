"""Console script for onthefly."""
import sys
import click
from .onthefly import onthefly


@click.command()
@click.argument('filename', type=click.Path(exists=True))
def main(filename):
    """Emulates typing each character contained inside FILENAME"""
    onthefly(filename)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
