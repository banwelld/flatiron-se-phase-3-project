import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from modules.user_sentinels import USER_CANCEL
from modules.get_config import NAV_OPS_CONFIG as NAV_CONFIG
from modules.get_confirmation import get_confirmation
from util.helpers import render_header
from strings.tint_string import tint_string
from strings.display_messages import EXIT_MSG, QUIT_PROMPT


# control flow


def quit_program():
    render_header(
        NAV_CONFIG["quit_program"]["display"].get("title"),
        None,
        entity_selected=False,
        ctrl_c_cancel=False,
    )

    if not get_confirmation(tint_string("plain", QUIT_PROMPT), False):
        return USER_CANCEL

    print()
    print(tint_string("title", EXIT_MSG) + "\n")
    exit()
