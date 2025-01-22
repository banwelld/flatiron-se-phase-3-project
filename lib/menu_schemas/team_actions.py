from helpers import (
    quit_program,
)

team_actions = {
    "menu_title": "Team Actions",
    "menu_items": [
        {
            "option": "Recruit Member",
            # "action": add_member_to_team,
        },
        {
            "option": "Remove Member",
            # "action": remove_member_from_team,
        },
        {
            "option": "Assign Captain",
            # "action": assign_team_captain,
        },
        {
            "option": "Update Team Name",
            # "action": update_team_name,
        },
        {
            "option": "Delete Team",
            # "action": delete_team,
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