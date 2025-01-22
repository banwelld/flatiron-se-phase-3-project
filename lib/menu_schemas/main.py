from dynamic_menu import dynamic_menu
from menu_schemas.member_actions import member_actions
from menu_schemas.team_actions import team_actions
from menu_schemas.member_search import member_search
from menu_schemas.team_search import team_search
from helpers import (
    quit_program,
    display_item_creation,
    member_select_menu,
)

main_menu = {
    "menu_title": "Main Menu",
    "menu_items": [
        {
            "option": "Member Actions",
            "action": member_select_menu,
        },  
        {
            "option": "Team Actions",
            "action": lambda: dynamic_menu(team_actions),
        },
        {
            "option": "Find Active Member",
            "action": lambda: dynamic_menu(member_search),
        },
        {
            "option": "Find Active Team",
            "action": lambda: dynamic_menu(team_search),
        },
        {
            "option": "Enroll New Member",
            "action": lambda: display_item_creation("member"),
        },
        {
            "option": "Enroll New Team",
            "action": lambda: display_item_creation("team"),
        },
    ],
    "nav_options": [
        {
            "option": "Exit Program",
            "selector": "x",
            "action": quit_program,
        },
    ],
}