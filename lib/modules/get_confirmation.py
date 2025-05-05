import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from util.helpers import (
    get_user_input_std,
    clear_cli,
)
from util.warnings import warn_invalid_selection
from strings.display_messages import YN_PROMPT


# ui rendering


def render_confirmation_prompt(prompt_text: str):
    print()
    print(prompt_text)
    print()


# response validation


def validate_confirmation_response(response: str):
    if response in ("y", "n"):
        return True
    warn_invalid_selection()
    return False


# control flow


def main(prompt_text: str, do_clear_screen: bool = True) -> bool:
    if do_clear_screen:
        clear_cli()

    render_confirmation_prompt(prompt_text)

    exit_loop = False

    while not exit_loop:
        response = get_user_input_std(YN_PROMPT).lower()
        exit_loop = validate_confirmation_response(response)

    return True if response == "y" else False
