from models.member import Member
from models.team import Team
from dynamic_menu import (
    render_menu,
    goto_assign_member,
    goto_remove_member,
    member_actions_via_select,
    team_actions_via_select,
)
from helpers import (
    create_new_member,
    create_new_team,
    update_first_name,
    update_last_name,
    update_team_name,
    do_input_operation,
)

# menu item lists

main = [
    {
        "option": "Member Actions",
        "action": member_actions_via_select,
    },  
    {
        "option": "Team Actions",
        "action": team_actions_via_select,
    },
    {
        "option": "Enroll New Member",
        "action": lambda: do_input_operation(create_new_member),
    },
    {
        "option": "Enroll New Team",
        "action": lambda: do_input_operation(create_new_team),
    },
]

mem_actions = [
    {
        "option": "Find Active Member By Name",
        "action": lambda: render_menu(mem_search, "Find a Member"),
    },
    {
        "option": "Find Active Member By ID",
        "action": lambda: render_menu(mem_search, "Find a Member"),
    },
    {
        "option": "Update First Name",
        "action": lambda: do_input_operation(update_first_name),
    },
    {
        "option": "Update Last Name",
        "action": lambda: do_input_operation(update_last_name),
    },
    {
        "option": "Assign to Team",
        "action": goto_assign_member,
    },
    {
        "option": "Remove from Team",
        "action": goto_remove_member,
    },
    {
        "option": "Delete Member",
        # "action": delete_member,
    },
]

team_actions = [
    {
        "option": "Find Team By Name",
        "action": lambda: render_menu(team_search, "Find a Team"),
    },
    {
        "option": "Find Team By ID",
        "action": lambda: render_menu(team_search, "Find a Team"),
    },
    {
        "option": "Recruit Member",
        "action": goto_assign_member,
    },
    {
        "option": "Remove Member",
        "action": goto_remove_member,
    },
    {
        "option": "Assign Captain",
        # "action": assign_team_captain,
    },
    {
        "option": "Update Team Name",
        "action": lambda: do_input_operation(update_team_name),
    },
    {
        "option": "Delete Team",
        # "action": delete_team,
    },
]