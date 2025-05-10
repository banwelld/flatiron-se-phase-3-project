import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from util.helpers import get_input_with_prompt
from util.warnings import warn_invalid_selection
from strings.display_messages import YN_PROMPT


def validate_confirmation_response(response: str):
    if response in ("y", "n"):
        return True
    warn_invalid_selection()
    return False


def main() -> bool:
    exit_loop = False
    while not exit_loop:
        response = get_input_with_prompt(YN_PROMPT).lower()
        exit_loop = validate_confirmation_response(response)
    return True if response == "y" else False
