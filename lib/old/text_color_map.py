text_color_map = {
    "angry": lambda text: f"\x1b[38;2;255;70;95m{text}\x1b[0m",
    "prompt": lambda text: f"\x1b[38;2;180;210;255m{text}\x1b[0m",
    "fresh": lambda text: f"\x1b[38;2;102;204;0m{text}\x1b[0m",
    "ask": lambda text: f"\x1b[38;2;0;180;190m{text}\x1b[0m",
    "nope": lambda text: f"\x1b[38;2;255;147;0m{text}\x1b[0m",
    "oops": lambda text: f"\x1b[38;2;255;220;0m{text}\x1b[0m",
    "option": lambda text: f"\x1b[38;2;230;230;230m{text}\x1b[0m",
    "plain": lambda text: f"\x1b[38;2;180;165;140m{text}\x1b[0m",
    "title": lambda text: f"\x1b[38;2;0;253;255m{text}\x1b[0m",
}
