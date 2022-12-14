#!/usr/bin/python3

# The events (key presses releases and repeats), are captured with evdev,
# and then injected back with uinput.

from evdev import UInput, ecodes, InputDevice, list_devices
from configparser import ConfigParser
import time, appdirs, sys
from pathlib import Path

time.sleep(0.1) # give time for packages to initialize properly

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

# Define the keys that can be used to indicate when to type the next character
# These name definitions are defined in /usr/include/linux/input-event-codes.h
WRITE_NEXT_CHAR_KEYS = [
    ecodes.KEY_A,
    ecodes.KEY_S,
    ecodes.KEY_D,
    ecodes.KEY_F,
    ecodes.KEY_J,
    ecodes.KEY_K,
    ecodes.KEY_L,
    ecodes.KEY_SEMICOLON,
]

def read_input_file(input_file):
    with open(input_file, encoding="utf-8") as f:
        chars = f.read()
    return chars

def create_config_file(filepath):
    Path(Path(filepath).parent).mkdir(parents=True, exist_ok=True) # create dirs to config file if necessary
    Path(filepath).touch() # create an empty config file if it doesn't exist

def update_config_file(keyboard_device_path, filepath):
    config = ConfigParser()
    config['DEFAULT'] = {'keyboard_device_path': keyboard_device_path}
    with open(filepath, 'w') as f:
        config.write(f) # store config in `filepath`

def read_config_keyboard_device_path(filepath):
    config = ConfigParser()
    config.read(filepath)
    try:
        return config['DEFAULT']['keyboard_device_path']
    except:
        return None

def simulate_key(ui, code, keystate):
    ui.write(ecodes.EV_KEY, code, keystate)
    ui.syn()

def simulate_key_press(ui, code):
    ui.write(ecodes.EV_KEY, code, 1)
    ui.syn()

def simulate_key_release(ui, code):
    ui.write(ecodes.EV_KEY, code, 0)
    ui.syn()

def simulate_key_stroke(ui, code):
    simulate_key_press(ui, code)
    simulate_key_release(ui, code)

def simulate_unicode_input(ui, unicode):
    # Press Control+Shift+U
    simulate_key_press(ui, ecodes.KEY_LEFTCTRL)
    simulate_key_press(ui, ecodes.KEY_LEFTSHIFT)
    simulate_key_press(ui, ecodes.KEY_U)
    simulate_key_release(ui, ecodes.KEY_U)
    simulate_key_release(ui, ecodes.KEY_LEFTSHIFT)
    simulate_key_release(ui, ecodes.KEY_LEFTCTRL)

    # Write each hex digit
    for hex_digit in '%X' % ord(unicode):
        keycode = getattr(ecodes, 'KEY_%s' % hex_digit)
        simulate_key_press(ui, keycode)
        simulate_key_release(ui, keycode)

    # Press Enter
    simulate_key_press(ui, ecodes.KEY_ENTER)
    simulate_key_release(ui, ecodes.KEY_ENTER)

def onthefly(input_file, keyboard_device_path):

    config_filepath = appdirs.user_config_dir() + '/onthefly/config.cfg'
    create_config_file(config_filepath)

    # If `keyboard_device_path` was provided, store it in `config_filepath`
    if keyboard_device_path: update_config_file(keyboard_device_path, config_filepath)

    # Read the `keyboard_device_path` stored in the config file (returns None no entry is found)
    keyboard_device_path = read_config_keyboard_device_path(config_filepath)

    if keyboard_device_path in list_devices():
        dev = InputDevice(keyboard_device_path)
    else:
        print("""Error: No keyboard found.

Use
    $ sudo python -m evdev.evtest
to find the device path of your keyboard and pass it to the `keyboard` option when invoking onthefly, e.g.:
    $ sudo onthefly --keyboard="/dev/input/event7" /path/to/file
""")
        sys.exit()

    chars = read_input_file(input_file) # read all chars in the input file
    char_idx = 0 # indicates the next character to be emulated

    dev.grab() # other applications will be unable to receive events until the keyboard device is released

    with UInput.from_device(dev, name='onthefly') as ui: # create a new "virtual" keyboard
        for event in dev.read_loop():  # read events from the "real" keyboard
            if event.type == ecodes.EV_KEY:  # only process "key" events

                ak = dev.active_keys() # get the active keys (keys that are being pressed down)

                # Exit on pressing F9 or when all chars have been written.
                if (event.code == ecodes.KEY_F9) or (char_idx == len(chars)):
                    dev.ungrab() # release the keybaord device so that other applications can receive events
                    break

                # Forward the event if any of the following "key modifiers" is being pressed
                elif (ecodes.KEY_LEFTCTRL in ak) or (ecodes.KEY_LEFTMETA in ak) or (ecodes.KEY_LEFTALT in ak):
                    simulate_key(ui, event.code, event.value)

                elif event.code == ecodes.KEY_BACKSPACE:
                    # Simulate a backspace only on key presses
                    if event.value == 1: 
                        char_idx -= 1 # decrement counter
                        simulate_key_stroke(ui, ecodes.KEY_BACKSPACE)
                    else:
                        continue # ignore key releases

                # Simulate press/release of next char if the key is inside of the WRITE_NEXT_CHAR_KEYS set
                elif event.code in WRITE_NEXT_CHAR_KEYS:
                    # Simulate next char only on key presses
                    if event.value == 1: 
                        # Is the current char in the "no-shift" ascii table?
                        if chars[char_idx] in ascii2keycode:
                            remapped_code = ascii2keycode.get(chars[char_idx])
                            simulate_key_stroke(ui, remapped_code)
                        # No, so is it in the "shift" ascii table?
                        elif chars[char_idx] in shift_ascii2keycode:
                            remapped_code = shift_ascii2keycode.get(chars[char_idx])
                            simulate_key_press(ui, ecodes.KEY_LEFTSHIFT)
                            simulate_key_stroke(ui, remapped_code)
                            simulate_key_release(ui, ecodes.KEY_LEFTSHIFT)
                        # No, then it must be a Unicode char. Have I mapped this Unicode char to custom behavior?
                        elif ord(chars[char_idx]) == 0x2408: # ␈
                            simulate_key_stroke(ui, ecodes.BACKSPACE)
                        elif ord(chars[char_idx]) == 0x2190: # ←
                            simulate_key_stroke(ui, ecodes.KEY_LEFT)
                        elif ord(chars[char_idx]) == 0x2191: # ↑
                            simulate_key_stroke(ui, ecodes.KEY_UP)
                        elif ord(chars[char_idx]) == 0x2192: # →
                            simulate_key_stroke(ui, ecodes.KEY_RIGHT)
                        elif ord(chars[char_idx]) == 0x2193: # ↓
                            simulate_key_stroke(ui, ecodes.KEY_DOWN)
                        elif ord(chars[char_idx]) == 0x21F1: # ⇱
                            simulate_key_stroke(ui, ecodes.KEY_HOME)
                        elif ord(chars[char_idx]) == 0x21F2: # ⇲
                            simulate_key_stroke(ui, ecodes.KEY_END)
                        elif ord(chars[char_idx]) == 0x21D0: # ⇐
                            simulate_key_press(ui, ecodes.KEY_LEFTSHIFT)
                            simulate_key_stroke(ui, ecodes.KEY_LEFT)
                            simulate_key_release(ui, ecodes.KEY_LEFTSHIFT)
                        elif ord(chars[char_idx]) == 0x21D1: # ⇑
                            simulate_key_press(ui, ecodes.KEY_LEFTSHIFT)
                            simulate_key_stroke(ui, ecodes.KEY_UP)
                            simulate_key_release(ui, ecodes.KEY_LEFTSHIFT)
                        elif ord(chars[char_idx]) == 0x21D2: # ⇒
                            simulate_key_press(ui, ecodes.KEY_LEFTSHIFT)
                            simulate_key_stroke(ui, ecodes.KEY_RIGHT)
                            simulate_key_release(ui, ecodes.KEY_LEFTSHIFT)
                        elif ord(chars[char_idx]) == 0x21D3: # ⇓
                            simulate_key_press(ui, ecodes.KEY_LEFTSHIFT)
                            simulate_key_stroke(ui, ecodes.KEY_DOWN)
                            simulate_key_release(ui, ecodes.KEY_LEFTSHIFT)
                        elif ord(chars[char_idx]) == 0x21e4: # ⇤
                            simulate_key_press(ui, ecodes.KEY_LEFTCTRL)
                            simulate_key_press(ui, ecodes.KEY_LEFTSHIFT)
                            simulate_key_stroke(ui, ecodes.KEY_I)
                            simulate_key_release(ui, ecodes.KEY_LEFTSHIFT)
                            simulate_key_release(ui, ecodes.KEY_LEFTCTRL)
                        elif ord(chars[char_idx]) == 0x21e5: # ⇥
                            simulate_key_press(ui, ecodes.KEY_LEFTCTRL)
                            simulate_key_stroke(ui, ecodes.KEY_I)
                            simulate_key_release(ui, ecodes.KEY_LEFTCTRL)
                        # No, then lets just enter the unicode char using the virtual keyboard
                        else:
                            simulate_unicode_input(ui, chars[char_idx])

                        char_idx += 1 # increment counter
                    else:
                        continue # ignore key releases
                else:
                    simulate_key(ui, event.code, event.value) # forward any other key events
            else:
                # Forward OTHER type of events (e.g. SYNs)
                ui.write(event.type, event.code, event.value)
                ui.syn()
