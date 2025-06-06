import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from util.helpers import render_warning
from strings.display_messages import (
    INVALID_SELECTION,
    INVALID_NAME_CHAR,
    INVALID_NAME_LEN,
    INVALID_DATE_FORMAT,
    INVALID_DATE,
    INVALID_OPTION,
    TEAM_FULL,
    TEAM_EMPTY,
)


def warn_invalid_selection():
    render_warning(INVALID_SELECTION)


def warn_invalid_char():
    render_warning(INVALID_NAME_CHAR)


def warn_length_invalid():
    render_warning(INVALID_NAME_LEN)


def warn_invalid_date_format():
    render_warning(INVALID_DATE_FORMAT)


def warn_date_invalid():
    render_warning(INVALID_DATE)


def warn_team_full():
    render_warning(TEAM_FULL)


def warn_team_empty():
    render_warning(TEAM_EMPTY)


def warn_invalid_option():
    render_warning(INVALID_OPTION, enter_to_continue=True)
