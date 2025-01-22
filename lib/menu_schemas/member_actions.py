from helpers import (
    quit_program,
)

member_actions = {
    "menu_title": "Member Actions",
    "menu_items": [
        {
            "option": "Update Member Name",
            # "action": update_member_name,
        },
        {
            "option": "Assign to Team",
            # "action": add_member_to_team,
        },
        {
            "option": "Remove from Team",
            # "action": remove_member_from_team,
        },
        {
            "option": "Delete Member",
            # "action": delete_member,
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