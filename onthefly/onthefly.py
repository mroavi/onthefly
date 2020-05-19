#!/usr/bin/python3

# The events (key presses releases and repeats), are captured with evdev,
# and then injected back with uinput.

# To bundle an executable run:
#   pyinstaller -F onthefly.py

# You need to install evdev with a package manager or pip3.
from evdev import UInput, ecodes, InputDevice, list_devices
import click
import time

# Give time for packages to initialize properly
time.sleep(0.1)

def onthefly(input_file):

    file_characters = [] # used to store all characters in the input file
    current_char_idx = 0 # indicates the next character to be emulated

    ascii2keycode = {
        None:0, u'ESC': 1, u'1': 2, u'2': 3, u'3': 4, u'4': 5, u'5': 6, u'6': 7, u'7': 8, u'8': 9,
        u'9': 10, u'0': 11, u'-': 12, u'=': 13, u'BKSP': 14, u'TAB': 15, u'q': 16, u'w': 17, u'e': 18, u'r': 19,
        u't': 20, u'y': 21, u'u': 22, u'i': 23, u'o': 24, u'p': 25, u'[': 26, u']': 27, u'\n': 28, u'LCTRL': 29,
        u'a': 30, u's': 31, u'd': 32, u'f': 33, u'g': 34, u'h': 35, u'j': 36, u'k': 37, u'l': 38, u';': 39,
        u'\'': 40, u'`': 41, u'LSHFT': 42, u'\\': 43, u'z': 44, u'x': 45, u'c': 46, u'v': 47, u'b': 48, u'n': 49,
        u'm': 50, u',': 51, u'.': 52, u'/': 53, u'RSHFT': 54, u'LALT': 56, u' ': 57, u'RALT': 100
    }

    shift_ascii2keycode= {
        None: 0, u'ESC': 1, u'!': 2, u'@': 3, u'#': 4, u'$': 5, u'%': 6, u'^': 7, u'&': 8, u'*': 9,
        u'(': 10, u')': 11, u'_': 12, u'+': 13, u'BKSP': 14, u'TAB': 15, u'Q': 16, u'W': 17, u'E': 18, u'R': 19,
        u'T': 20, u'Y': 21, u'U': 22, u'I': 23, u'O': 24, u'P': 25, u'{': 26, u'}': 27, u'CRLF': 28, u'LCTRL': 29,
        u'A': 30, u'S': 31, u'D': 32, u'F': 33, u'G': 34, u'H': 35, u'J': 36, u'K': 37, u'L': 38, u':': 39,
        u'"': 40, u'~': 41, u'LSHFT': 42, u'|': 43, u'Z': 44, u'X': 45, u'C': 46, u'V': 47, u'B': 48, u'N': 49,
        u'M': 50, u'<': 51, u'>': 52, u'?': 53, u'RSHFT': 54, u'LALT': 56,  u' ': 57, u'RALT': 100
    }

    def read_next_character(f):
        """Reads one character from the given textfile"""
        c = f.read(1)
        while c:
            yield c
            c = f.read(1)

    with open(input_file, encoding="utf-8") as f:
        """Opens a file and store each character as an element of a list"""
        for c in read_next_character(f):
            file_characters.append(c)

    # Define the keys that can be used to indicate when to type the next character
    WRITE_NEXT_CHAR_KEYS = [
        # Let's intercerpt the characters asdfjkl;
        ecodes.KEY_A,
        ecodes.KEY_S,
        ecodes.KEY_D,
        ecodes.KEY_F,
        ecodes.KEY_J,
        ecodes.KEY_K,
        ecodes.KEY_L,
        ecodes.KEY_SEMICOLON,
    ]
    # The names can be found running evtest from the terminal:
    #    > sudo python -m evdev.evtest

    # The keyboard name we will intercept the events for. Obtainable with evtest.
    MATCH = 'Logitech K330' # mrv
    # Find all input devices.
    devices = [InputDevice(fn) for fn in list_devices()]
    # Limit the list to those containing MATCH and pick the first one.
    dev = [d for d in devices if MATCH in d.name][0]

    dev.grab() # Grab, i.e. prevent the keyboard from emitting original events.

    # Create a new keyboard mimicking the original one.
    with UInput.from_device(dev, name='onthefly') as ui:
        for event in dev.read_loop():  # Read events from original keyboard.
            if event.type == ecodes.EV_KEY:  # Process key events.
                if event.code == ecodes.KEY_PAUSE and event.value == 1 \
                        or current_char_idx == len(file_characters):
                    # Exit on pressing PAUSE or when all characters have been written.
                    dev.ungrab() # mrv
                    break

                elif event.code == ecodes.KEY_BACKSPACE and event.value ==1:
                    # Decrement counter
                    current_char_idx -= 1
                    # Passthrough key event unmodified
                    ui.write(ecodes.EV_KEY, event.code, 1)
                    ui.write(ecodes.EV_KEY, event.code, 0)
                    ui.syn()

                # Write next char when:
                #   - current key pressed is in the set of permitted keys
                #   - Control key is not pressed
                #   - current action is a press and not a release
                elif event.code in WRITE_NEXT_CHAR_KEYS \
                        and ecodes.KEY_LEFTCTRL not in dev.active_keys() \
                        and event.value == 1:
                    # Check if we need to press shift
                    if file_characters[current_char_idx] in ascii2keycode:
                        # No, we don't. Lookup the key we want to press/release
                        remapped_code = ascii2keycode[file_characters[current_char_idx]]
                        ui.write(ecodes.EV_KEY, remapped_code, 1)
                        ui.syn()
                        ui.write(ecodes.EV_KEY, remapped_code, 0)
                        ui.syn()
                    elif file_characters[current_char_idx] in shift_ascii2keycode:
                        # Yes, we do. Lookup the key we want to press/release
                        remapped_code = shift_ascii2keycode[file_characters[current_char_idx]]
                        ui.write(ecodes.EV_KEY, ecodes.KEY_LEFTSHIFT, 1) # press shift
                        ui.syn()
                        ui.write(ecodes.EV_KEY, remapped_code, 1)
                        ui.syn()
                        ui.write(ecodes.EV_KEY, remapped_code, 0)
                        ui.syn()
                        ui.write(ecodes.EV_KEY, ecodes.KEY_LEFTSHIFT, 0) # release shift
                        ui.syn()
                    else:
                        # The character is not in either dictionary, then it must be a unicode
                        # Press Control+Shift+U
                        ui.write(ecodes.EV_KEY, ecodes.KEY_LEFTCTRL, 1)
                        ui.syn()
                        ui.write(ecodes.EV_KEY, ecodes.KEY_LEFTSHIFT, 1)
                        ui.syn()
                        ui.write(ecodes.EV_KEY, ecodes.KEY_U, 1)
                        ui.syn()
                        ui.write(ecodes.EV_KEY, ecodes.KEY_U, 0)
                        ui.syn()
                        ui.write(ecodes.EV_KEY, ecodes.KEY_LEFTSHIFT, 0)
                        ui.syn()
                        ui.write(ecodes.EV_KEY, ecodes.KEY_LEFTCTRL, 0)
                        ui.syn()

                        # Write each hex digit
                        for hex_digit in '%X' % ord(file_characters[current_char_idx]):
                            keycode = getattr(ecodes, 'KEY_%s' % hex_digit)
                            ui.write(ecodes.EV_KEY, keycode, 1)
                            ui.syn()
                            ui.write(ecodes.EV_KEY, keycode, 0)
                            ui.syn()

                        # Press Enter
                        ui.write(ecodes.EV_KEY, ecodes.KEY_ENTER, 1)
                        ui.write(ecodes.EV_KEY, ecodes.KEY_ENTER, 0)
                        ui.syn()

                    # Increment counter
                    current_char_idx += 1
                else:
                    # Passthrough other key events unmodified.
                    ui.write(ecodes.EV_KEY, event.code, event.value)
                    ui.syn()
            else:
                # Passthrough other events unmodified (e.g. SYNs).
                ui.write(event.type, event.code, event.value)
                ui.syn()

if __name__ == '__main__':
    onthefly()

# Convert the scancode into a ASCII code
# https://stackoverflow.com/questions/19732978/how-can-i-get-a-string-from-hid-device-in-python-with-evdev

# python-evdev tutorial:
# https://python-evdev.readthedocs.io/en/latest/tutorial.html#

# example_remap.py (does not work out of the box)
# https://gist.github.com/paulo-raca/0e772864013b88de205a
