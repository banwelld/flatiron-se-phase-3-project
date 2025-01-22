from helpers import (
    quit_program,
)

team_search = {
    "menu_title": "Find a Team",
    "menu_items": [
        {
            "option": "By Name",
            # "action": find_team_by_name,
        },
        {
            "option": "By Team ID",
            # "action": find_team_by_id,
        },
        {
            "option": "Select from List",
            # "action": find_team_in_list,
        },
    ],
    "nav_options": [
        {
            "option": "Back to Previous Menu",
            "selector": "b",
            "action": None,
        },
        {
            "option": "Exit Program",
            "selector": "x",
            "action": quit_program,
        },
    ],
}