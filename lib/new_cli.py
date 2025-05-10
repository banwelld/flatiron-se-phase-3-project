import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from classes.step_context import StepContext
from models.participant import Participant
from models.team import Team
from modules.process_menu_response import main as process_menu_response
from modules.create_entity import main as create_entity
from modules.get_confirmation import main as get_confirmation
from modules.update_entity import main as update_entity
from modules.team_assignment import (
    main as assign_to_team,
)
from config.get_config import (
    MENU_OPS_CONFIG,
    NAV_OPS_CONFIG,
    OPS_CONFIG,
)
from util.nav_sentinels import (
    USER_RESET,
    USER_BACK,
    USER_QUIT,
)
from strings.display_messages import EXIT_MSG
from util.helpers import (
    generate_disp_text,
    render_header,
    render_menu,
    render_team_participant_list,
    render_save_prompt,
)


def create_team(context):
    c_state = context.state
    render_header(
        OPS_CONFIG["create_team"].get("title_suffix"),
        OPS_CONFIG["create_team"].get("instruction"),
        generate_disp_text(c_state["sel_participant"], "fresh"),
        generate_disp_text(c_state["sel_team"], "fresh"),
        ctrl_c_cancel=True,
    )
    new_team = create_entity(Team)

    if isinstance(new_team, Team):
        resolve_nav_sentinel(new_team)

    new_state = c_state.copy()
    new_state["sel_team"] = new_team
    new_state["save_prompt"] = f"Save new team: {generate_disp_text(new_team)}?"
    new_state["exec_func"] = new_team.save
    context.push(get_confirmation, new_state)


def create_participant(context):
    c_state = context.state
    render_header(
        OPS_CONFIG["create_participant"].get("title_suffix"),
        OPS_CONFIG["create_participant"].get("instruction"),
        generate_disp_text(c_state["sel_participant"], "fresh"),
        generate_disp_text(c_state["sel_team"], "fresh"),
        ctrl_c_cancel=True,
    )
    new_participant = create_entity(Participant)

    if not isinstance(new_participant, Participant):
        resolve_nav_sentinel(new_participant)

    new_state = c_state.copy()
    new_state["sel_participant"] = new_participant
    new_state["save_prompt"] = (
        f"Save new participant: {generate_disp_text(new_participant)}?"
    )
    new_state["exec_func"] = new_participant.save
    context.push(get_confirmation, new_state)


def recruit_free_agent(context):
    c_state = context.state
    participant = assign_to_team(
        c_state["sel_participant"],
        c_state["sel_team"],
    )
    if not isinstance(participant, Participant):
        return resolve_nav_sentinel(participant)

    new_state = c_state.copy()
    new_state["sel_participant"] = participant
    new_state["save_prompt"] = (
        f"Move {generate_disp_text(participant)} to {generate_disp_text(c_state['sel_team'])}?"
    )
    new_state["exec_func"] = participant.update
    context.push(get_confirmation, new_state)


def remove_participant(context):
    c_state = context.state
    participant = assign_to_team(
        c_state["sel_participant"],
        c_state["free_agent_team"],
    )
    if not isinstance(participant, Participant):
        return resolve_nav_sentinel(participant)

    new_state = c_state.copy()
    new_state["sel_participant"] = participant
    new_state["save_prompt"] = (
        f"Remove {generate_disp_text(participant)} from {generate_disp_text(c_state['sel_team'])}?"
    )
    new_state["exec_func"] = participant.update
    context.push(get_confirmation, new_state)


def delete_team(context):
    c_state = context.state
    new_state = c_state.copy()
    new_state["save_prompt"] = (
        f"Delete team: {generate_disp_text(c_state['sel_team'])}?"
    )

    # dedicated function to be passed forward to persist the member reassignment and team deletion
    def delete_team_reassign_all():
        for p in new_state["team_participants"]:
            p.team_id = new_state["free_agent_team"].id
            p.update()
        new_state["sel_team"].delete()

    new_state["exec_func"] = delete_team_reassign_all
    context.push(get_confirmation, new_state)


def delete_participant(context):
    c_state = context.state
    new_state = c_state.copy()
    new_state["save_prompt"] = (
        f"Delete participant: {generate_disp_text(c_state['sel_participant'])}?"
    )
    new_state["exec_func"] = c_state["sel_participant"].delete
    context.push(get_confirmation)


def update_participant_first_name(context):
    c_state = context.state
    render_header(
        OPS_CONFIG["update_participant_first_name"].get("title_suffix"),
        OPS_CONFIG["update_participant_first_name"].get("instruction"),
        generate_disp_text(c_state["sel_participant"], "fresh"),
        generate_disp_text(c_state["sel_team"], "fresh"),
        ctrl_c_cancel=True,
    )
    participant = update_entity(c_state["sel_participant"], "first_name")

    if not isinstance(participant, Participant):
        return resolve_nav_sentinel(participant)

    new_state = c_state.copy()
    new_state["save_prompt"] = (
        f"Update participant's first name to: {generate_disp_text(participant.first_name)}?"
    )
    new_state["exec_func"] = participant.update
    context.push(get_confirmation, new_state)


def update_participant_last_name(context):
    c_state = context.state
    render_header(
        OPS_CONFIG["update_participant_last_name"].get("title_suffix"),
        OPS_CONFIG["update_participant_last_name"].get("instruction"),
        generate_disp_text(c_state["sel_participant"], "fresh"),
        generate_disp_text(c_state["sel_team"], "fresh"),
        ctrl_c_cancel=True,
    )
    participant = update_entity(c_state["sel_participant"], "last_name")

    if not isinstance(participant, Participant):
        return resolve_nav_sentinel(participant)

    new_state = c_state.copy()
    new_state["save_prompt"] = (
        f"Update participant's lsst name to: {generate_disp_text(participant.last_name)}?"
    )
    new_state["exec_func"] = participant.update
    context.push(get_confirmation, new_state)


def update_team_name(context):
    c_state = context.state
    render_header(
        OPS_CONFIG["update_team_name"].get("title_suffix"),
        OPS_CONFIG["update_team_name"].get("instruction"),
        generate_disp_text(c_state["sel_participant"], "fresh"),
        generate_disp_text(c_state["sel_team"], "fresh"),
        ctrl_c_cancel=True,
    )
    team = update_entity(c_state["sel_team"], "name")

    if not isinstance(team, Team):
        return resolve_nav_sentinel(team)

    new_state = c_state.copy()
    new_state["save_prompt"] = f"Update team name to: {generate_disp_text(team.name)}?"
    new_state["exec_func"] = team.update
    context.push(get_confirmation, new_state)


def select_team(context):
    c_state = context.state
    c_state["all_teams"] = Team.fetch_all()
    render_header(
        MENU_OPS_CONFIG["team"].get("title_suffix"),
        MENU_OPS_CONFIG["team"].get("instruction"),
        generate_disp_text(c_state["sel_participant"], "fresh"),
        generate_disp_text(c_state["sel_team"], "fresh"),
        ctrl_c_cancel=False,
    )
    menu_options = (
        (index, generate_disp_text(t, "option"), t)
        for index, t in enumerate(c_state["all_teams"], start=1)
    )
    nav_options = (
        (op[0].upper(), attrs.get("menu_text"), op)
        for op, attrs in NAV_OPS_CONFIG.items()
    )
    render_menu(menu_options, nav_options)
    response = process_menu_response(menu_options, nav_options)

    if not isinstance(response, Participant):
        return resolve_nav_sentinel(response)

    new_state = c_state.copy()
    new_state["sel_team"] = response
    new_state["sel_team_participants"] = c_state["sel_team"].fetch_participants()
    context.push(select_operation, new_state)


def select_operation(context):
    c_state = context.state
    render_header(
        MENU_OPS_CONFIG["operation"].get("title_suffix"),
        MENU_OPS_CONFIG["operation"].get("instruction"),
        generate_disp_text(c_state["sel_participant"], "fresh"),
        generate_disp_text(c_state["sel_team"], "fresh"),
        ctrl_c_cancel=False,
    )
    render_team_participant_list(c_state)
    menu_options = (
        (index, generate_disp_text(attrs.get("menu_text"), "option"), op)
        for index, (op, attrs) in enumerate(OPS_CONFIG.items(), start=1)
    )
    nav_options = (
        (op[0].upper(), attrs.get("menu_text"), op)
        for op, attrs in NAV_OPS_CONFIG.items()
    )
    render_menu(menu_options, nav_options)
    response = process_menu_response(menu_options, nav_options)

    if not response in globals():
        return resolve_nav_sentinel(response)

    new_state = c_state.copy()
    new_state["operation"] = response
    next_step_func = (
        select_participant
        if OPS_CONFIG[new_state["operation"]].get("resolve_participants")
        else globals().get(new_state["operation"])
    )
    context.push(next_step_func, new_state)


def select_participant(context):
    c_state = context.state
    render_header(
        MENU_OPS_CONFIG["participant"].get("title_suffix"),
        MENU_OPS_CONFIG["participant"].get("instruction"),
        generate_disp_text(c_state["sel_participant"], "fresh"),
        generate_disp_text(c_state["sel_team"], "fresh"),
        ctrl_c_cancel=False,
    )
    if OPS_CONFIG[c_state["operation"]]["load_free_agents"]:
        c_state["free_agents"] = c_state["free_agent_team"].fetch_participants()

    participant_list = (
        c_state["free_agents"]
        if c_state["operation"] == "recruit_free_agent"
        else c_state["sel_team_participants"]
    )
    menu_options = (
        (index, generate_disp_text(p, "option"), p)
        for index, p in enumerate(participant_list)
    )
    nav_options = (
        (op[0].upper(), attrs.get("menu_text"), op)
        for op, attrs in NAV_OPS_CONFIG.items()
    )
    render_menu(menu_options, nav_options)
    response = process_menu_response(menu_options, nav_options)

    if isinstance(response, Participant):
        return resolve_nav_sentinel(response)

    new_state = c_state.copy()
    new_state["sel_participant"] = response
    op_func = globals().get(new_state["operation"])
    context.push(op_func, new_state)


def step_back(context):
    if context.can_go_back():
        _, saved_state = context.pop()
        context.state = saved_state


def confirm_persist(context):
    c_state = context.state
    render_save_prompt(c_state["save_prompt"])
    persist_change = c_state["exec_func"]
    if get_confirmation():
        persist_change()


def resolve_nav_sentinel(response):
    if response is USER_BACK:
        return step_back()
    elif response is USER_RESET:
        return context.restart()
    elif response is USER_QUIT:
        return context.stack.clear()


# initialize context object with first step
context = StepContext(select_team)


# stack flow loop
while context.stack:
    step_func = context.stack[-1][0]
    step_func(context)

print(f"\n{generate_disp_text(EXIT_MSG, 'title')}\n")
exit()
