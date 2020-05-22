onthefly
========

[![Build Status](https://img.shields.io/pypi/v/onthefly.svg)](https://pypi.python.org/pypi/onthefly)

[![asciicast](https://asciinema.org/a/1O1h6bm4KiQcYVCSduQtGIohD.svg)](https://asciinema.org/a/1O1h6bm4KiQcYVCSduQtGIohD)

onthefly allows you to emulate typing the contents of an input file by wildly pressing the *asdf jkl;* keys of your keyboard.
Great for live coding presentations.


Features
--------

* Unicode support
* Works with any text editor


Installation
------------

Install and update at system level using pip:

```bash
$ sudo python -m pip install onthefly
```

Usage
-----

Identify your keyboard with `evtest`:

```bash
$ sudo python -m evdev.evtest

ID  Device               Name                                ...
-------------------------------------------------------------...
0   /dev/input/event0    Lid Switch                          ...
1   /dev/input/event1    Power Button                        ...
2   /dev/input/event2    Sleep Button                        ...
3   /dev/input/event3    Power Button                        ...
4   /dev/input/event4    AT Translated Set 2 keyboard        ...
5   /dev/input/event5    Video Bus                           ...
6   /dev/input/event6    Logitech M215 2nd Gen               ...
7   /dev/input/event7    Logitech K330                       ...
8   /dev/input/event8    SynPS/2 Synaptics TouchPad          ...
.
.
.
```

From this output, we see that my keyboard is identified with the name `Logitech K330`.

Pass the name of your keyboard as an argument to the `keyboard` option when invoking onthefly for the first time.

```bash
$ sudo onthefly --keyboard="Logitech K330" /path/to/file
```

Note that onthefly needs to be run with sudo privileges in order to have access to the keyboard events:

The keyboard name is remembered so you do not have to re-enter it in future invokations:

```bash
$ sudo onthefly /path/to/file
```

Type the Pause/Break key to quit the program at any moment. Supports using the Backspace key to erase characters without going out of sync with respect to the input file.

License
-------

* Free software: MIT license


Credits
-------

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.