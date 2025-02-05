from models.member import Member
from models.team import Team
from ui_rendering import generate_menu, render_display_list
from helpers import (
    CLI_user_input_operation,
    show_active_team_roster,
    assign_team_id_to_current_member,
    remove_team_id_from_current_member,
    assign_captain_id_to_current_team,
    reemove_captain_id_from_current_team,
    delete_current_member,
    delete_current_team,
)

# menu item lists

main = [
    {
        "option": "Enroll New Member",
        "action": lambda: CLI_user_input_operation("new", Member),
    },
    {
        "option": "Enroll New Team",
        "action": lambda: CLI_user_input_operation("new", Team),
    },
    {
        "option": "View Member Master List",
        "action": lambda: render_display_list("Member", Member.fetch_all),
    },
    {
        "option": "View Team Master List",
        "action": lambda: render_display_list("Team", Team.fetch_all),
    },
    {
        "option": "Advanced Member Actions",
        "action": lambda: generate_menu(mem_actions, "member options"),
    },  
    {
        "option": "Advanced Team Actions",
        "action": lambda: generate_menu(team_actions, "team options"),
    },
]

mem_actions = [
    {
        "option": "Find Member By Name",
        "action": lambda: CLI_user_input_operation("name_search", Member),
    },
    {
        "option": "Find Member By ID",
        "action": lambda: CLI_user_input_operation("id_search", Member, "id"),
    },
    {
        "option": "Update First Name",
        "action": lambda: CLI_user_input_operation("update", Member, "first_name"),
    },
    {
        "option": "Update Last Name",
        "action": lambda: CLI_user_input_operation("update", Member, "last_name"),
    },
    {
        "option": "Assign to Team",
        "action": assign_team_id_to_current_member,
    },
    {
        "option": "Remove from Team",
        "action": remove_team_id_from_current_member,
    },
    {
        "option": "Delete Member",
        "action": delete_current_member,
    },
]

team_actions = [
    {
        "option": "Find Team By Name",
        "action": lambda: CLI_user_input_operation("name_search", Team),
    },
    {
        "option": "Find Team By ID",
        "action": lambda: CLI_user_input_operation("id_search", Team, "id"),
    },
    {
        "option": "Show Team Roster",
        "action": show_active_team_roster,
    },
    {
        "option": "Assign Captain",
        "action": assign_captain_id_to_current_team,
    },
    {
        "option": "Remove Captain",
        "action": reemove_captain_id_from_current_team,
    },
    {
        "option": "Update Team Name",
        "action": lambda: CLI_user_input_operation("update", Team, "name"),
    },
    {
        "option": "Delete Team",
        "action": delete_current_team,
    },
]