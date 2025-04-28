import json
from pathlib import Path

# open text color map (rgb values) for reading

color_map_path = Path(__file__).parent / "color_map.json"
with color_map_path.open("r", encoding="utf-8") as c:
    COLOR_MAP = json.load(c)


def tint_string(color_key: str, text_string: str) -> str:
    rgb_combo = COLOR_MAP[color_key]
    return f"\x1b[38;2;{rgb_combo}m{text_string}\x1b[0m"
