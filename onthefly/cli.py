"""Console script for onthefly."""
import sys
import click
from .onthefly import onthefly


@click.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--keyboard', help='The match string used to search for the keyboard.')
def main(filename, keyboard):
    """Emulates typing each character contained inside FILENAME"""
    onthefly(filename, keyboard)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
