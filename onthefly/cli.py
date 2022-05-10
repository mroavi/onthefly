"""Console script for onthefly."""
import sys
import click
from onthefly.onthefly import onthefly
from elevate import elevate


@click.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--keyboard', help='Your keyboard\'s device path. You can use `sudo evemu-record` to identify your keyboard\'s device path')
def main(filename, keyboard):
    """ Allows you to emulate typing the contents of an input file by wildly pressing the 'asdfjkl;' keys of your keyboard."""
    elevate(graphical=False)
    onthefly(filename, keyboard)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
