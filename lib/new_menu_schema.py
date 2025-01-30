from models.member import Member
from models.team import Team
from helpers import (
    add_new_member,
    add_new_team,
    update_member_firstname,
    update_member_lastname,
    update_team_name,
    assign_member_to_team,
    remove_member_from_team,
    search_member_by_id,
    search_team_by_id,
    search_member_by_name,
    search_team_by_name,
    select_member_from_roster,
    select_team_from_roster,
)

menu_items = [
    {
        "option": "Add New Member",
        "action": add_new_member,
        "needs_member": False,
        "Nneeds_team": False,
    },  
    {
        "option": "Add New Team",
        "action": add_new_team,
        "needs_member": False,
        "needs_team": False,
    },
    {
        "option": "Search for Member by Name",
        "action": search_member_by_name,
        "needs_member": False,
        "Nneeds_team": False,
    },
    {
        "option": "Search for Member by ID",
        "action": search_member_by_id,
        "needs_member": False,
        "needs_team": False,
    },
    {
        "option": "Select Member from Roster",
        "action": select_member_from_roster,
        "needs_member": False,
        "needs_team": False,
    },
    {
        "option": "Search for Team by Name",
        "action": search_team_by_name,
        "needs_member": False,
        "needs_team": False,
    },
    {
        "option": "Search for Team by ID",
        "action": search_team_by_id,
        "needs_member": False,
        "needs_team": False,
    },
    {
        "option": "Select Team from Roster",
        "action": select_team_from_roster,
        "needs_member": False,
        "needs_team": False,
    },
    {
        "option": "Change Member First Name",
        "action": update_member_firstname,
        "needs_member": True,
        "needs_team": False,
    },
    {
        "option": "Change Member last Name",
        "action": update_member_lastname,
        "needs_member": True,
        "needs_team": False,
    },
    {
        "option": "Change Team Name",
        "action": update_team_name,
        "needs_member": False,
        "needs_team": True,
    },
    {
        "option": "Assign Member to Team",
        "action": assign_member_to_team,
        "needs_member": True,
        "needs_team": True,
    },
    {
        "option": "Assign Team Captain",
        "action": None,
        "needs_member": True,
        "needs_team": True,
    },
    {
        "option": "Remove Member from Team",
        "action": remove_member_from_team,
        "needs_member": True,
        "needs_team": False,
    },
    {
        "option": "Delete Member Record",
        "action": None,
    },
    {
        "option": "Delete Team Record",
        "action": None,
    },
]
