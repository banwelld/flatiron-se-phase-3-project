from helpers import (
    quit_program,
)

member_search = {
    "menu_title": "Find a Member",
    "menu_items": [
        {
            "option": "By Name",
            # "action": find_member_by_name,
        },
        {
            "option": "By Birthday",
            # "action": find_member_by_dob,
        },
        {
            "option": "By Member ID",
            # "action": find_member_by_id,
        },
        {
            "option": "Select from List",
            # "action": find_member_in_list,
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