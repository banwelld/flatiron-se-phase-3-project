from util.helpers import render_warning
from strings.user_messages import (
    INVALID_SELECTION,
    INVALID_NAME_CHAR,
    INVALID_NAME_LEN,
    INVALID_DATE_FORMAT,
    INVALID_DATE,
    TEAM_FULL,
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
