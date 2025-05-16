import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from classes import StepContext
from models import Participant, Team
from modules import process_menu_response, get_attr_value
from config import (
    MENU_OPS_CONFIG,
    NAV_OPS_CONFIG,
    OPS_CONFIG,
)
from strings.display_messages import EXIT_MSG
from util.helpers import (
    generate_disp_text,
    fmt_participant_name,
    render_header,
    render_menu,
    render_result,
    fetch_teams,
    get_user_confirmation,
    clear_cli,
    back_to_op_select,
    resolve_nav_sentinel,
)
from util.warnings import (
    warn_invalid_option,
)

# navigation sentinals

USER_BACK = object()
USER_RESET = object()
USER_QUIT = object()

sentinels = (USER_BACK, USER_RESET, USER_QUIT)


# sort keys for participant and team lists
participant_sort = lambda p: (p.last_name, p.first_name)
team_sort = lambda t: t.name


# menu operations


def select_team(context):
    state = context.state
    state["competing_teams"], state["free_agent_team"] = fetch_teams()
    render_header(
        MENU_OPS_CONFIG["team"].get("title_suffix"),
        MENU_OPS_CONFIG["team"].get("instruction"),
        ctrl_c_cancel=False,
    )
    # create a list of tuples containing team names and objects
    team_options = [(t.name, t) for t in state["competing_teams"]]
    # extend menu_options with the create team operation
    all_options = team_options + list(
        (attrs.get("menu_text"), op)
        for op, attrs in OPS_CONFIG.items()
        if op == "create_team"
    )
    # transform menu_options into a tuple containing the previous tuples, now with indicies
    menu_options = tuple(
        (str(index), tup[0], tup[1]) for index, tup in enumerate(all_options, start=1)
    )
    # generate the quit nav option
    quit_opt = NAV_OPS_CONFIG.get("quit")
    quit_text = quit_opt.get("menu_text")
    # tuple inside a tuple because this is a collection of options with a length of 1
    nav_options = tuple(((quit_text[0], quit_text, "quit", quit_opt.get("format")),))
    render_menu(menu_options, nav_options)
    response = process_menu_response(
        menu_options, nav_options, back=USER_BACK, reset=USER_RESET, quit=USER_QUIT
    )
    if response in sentinels:
        return resolve_nav_sentinel(
            response, context, back=USER_BACK, reset=USER_RESET, quit=USER_QUIT
        )
    
    elif isinstance(response, Team):
        state["team"] = response
        state["team_name"] = generate_disp_text(response)
        state["team_participants"] = Participant.fetch(state["team"].id)
        context.push(select_operation)
        
    elif isinstance(response, str):
        if not response in globals():
            warn_invalid_option()
            return context.restart()
        next_step_func = globals().get(response)
        context.push(next_step_func)


def select_operation(context):
    state = context.state
    render_header(
        MENU_OPS_CONFIG["operation"].get("title_suffix"),
        MENU_OPS_CONFIG["operation"].get("instruction"),
        team_name=state["team_name"],
        team_roster=state["team_participants"],
        ctrl_c_cancel=False,
    )
    menu_options = tuple(
        (str(index), attrs.get("menu_text"), op)
        for index, (op, attrs) in enumerate(OPS_CONFIG.items())
        if op != "create_team"
    )
    nav_options = tuple(
        (op[0], attrs.get("menu_text"), op, attrs.get("format"))
        for op, attrs in NAV_OPS_CONFIG.items()
    )
    render_menu(menu_options, nav_options)
    response = process_menu_response(
        menu_options,
        nav_options,
        state["team"],
        len(state["team_participants"]),
        back=USER_BACK,
        reset=USER_RESET,
        quit=USER_QUIT
    )
    if response in sentinels:
        return resolve_nav_sentinel(
            response, context, back=USER_BACK, reset=USER_RESET, quit=USER_QUIT
        )

    state["operation"] = response
    next_step_func = (
        select_participant
        if OPS_CONFIG[response].get("resolve_participant")
        else globals().get(response)
    )
    context.push(next_step_func)


def select_participant(context):
    state = context.state
    need_free_agents = state["operation"] == "recruit_free_agent"
    render_header(
        OPS_CONFIG[state["operation"]].get("title_suffix"),
        MENU_OPS_CONFIG["participant"].get("instruction"),
        team_name=state["team_name"],
        team_roster=state["team_participants"] if need_free_agents else None,
        ctrl_c_cancel=False,
    )
    if OPS_CONFIG[state["operation"]]["load_free_agents"]:
        state["free_agents"] = state["free_agent_team"].fetch_participants()

    participant_list = (
        state["free_agents"] if need_free_agents else state["team_participants"]
    )
    menu_options = tuple(
        (str(index), fmt_participant_name(p.first_name, p.last_name), p)
        for index, p in enumerate(participant_list, start=1)
    )
    nav_options = tuple(
        (op[0], attrs.get("menu_text"), op, attrs.get("format"))
        for op, attrs in NAV_OPS_CONFIG.items()
    )
    render_menu(menu_options, nav_options)
    response = process_menu_response(
        menu_options, nav_options, back=USER_BACK, reset=USER_RESET, quit=USER_QUIT
    )
    if response in sentinels:
        return resolve_nav_sentinel(
            response, context, back=USER_BACK, reset=USER_RESET, quit=USER_QUIT
        )

    state["participant"] = response
    state["participant_name"] = generate_disp_text(response)
    op_func = globals().get(state["operation"])
    context.push(op_func)


# team and participant management operations


def create_team(context):
    state = context.state
    config = OPS_CONFIG["create_team"]
    render_header(
        config.get("title_suffix"), config.get("instruction"), ctrl_c_cancel=True
    )
    team_name = get_attr_value("team", Team.CONFIG.get("name"), USER_BACK)

    if team_name in sentinels:
        resolve_nav_sentinel(
            new_team, back=USER_BACK, reset=USER_RESET, quit=USER_QUIT
        )

    new_team = Team.create(team_name)
    save_prompt = f"Create team {generate_disp_text(new_team)}?"

    clear_cli()

    if is_confirmed := get_user_confirmation(save_prompt):
        new_team.save()
        state["team"] = new_team
        state["team_name"] = generate_disp_text(new_team)
        state["competing_teams"].append(new_team)
        state["competing_teams"].sort(key=team_sort)
        state["team_participants"] = []

    render_result(state.get("team_name"), config.get("success_msg"), is_confirmed)
    back_to_op_select(context, select_team, select_operation)


def create_participant(context):
    state = context.state
    config = OPS_CONFIG["create_participant"]
    render_header(
        config.get("title_suffix"),
        config.get("instruction"),
        team_name=state["team_name"],
        team_roster=state["team_participants"],
        ctrl_c_cancel=True,
    )
    # organize the init attrs into a dict
    init_attr = {
        attr: config
        for attr, config in Participant.CONFIG.items()
        if config.get("req_for_init")
    }
    # iterate through the dict to get values from the user for each attr
    attr_collection = {}
    for attr, config in init_attr.items():
        attr_collection[attr] = get_attr_value("participant", config, USER_BACK)
        if attr_collection[attr] in sentinels:
            return resolve_nav_sentinel(
                attr_collection[attr], context, back=USER_BACK, reset=USER_RESET, quit=USER_QUIT
            )

    new_participant = Participant.create(**attr_collection)
    save_prompt = (
        f"Create {generate_disp_text(new_participant)} "
        f"and assign to {state['team_name']}?"
    )
    clear_cli()

    if is_confirmed := get_user_confirmation(save_prompt):
        state["participant"] = new_participant
        setattr(state["participant"], "team_id", state["team"].id)
        new_participant.save()
        state["participant_name"] = generate_disp_text(state["participant"])
        state["team_participants"].append(state["participant"])
        state["team_participants"].sort(key=participant_sort)

    render_result(
        state.get("participant_name"), config.get("success_msg"), is_confirmed
    )
    back_to_op_select(context, select_team, select_operation)


def recruit_free_agent(context):
    state = context.state
    save_prompt = f"Assign {state['participant_name']} to {state['team_name']}?"

    clear_cli()

    if is_confirmed := get_user_confirmation(save_prompt):
        setattr(state["participant"], "team_id", state["team"].id)
        state["participant"].update()
        state["team_participants"].append(state["participant"])
        state["team_participants"].sort(key=participant_sort)

    render_result(
        state.get("participant_name"),
        OPS_CONFIG["recruit_free_agent"].get("success_msg"),
        is_confirmed,
    )
    back_to_op_select(context, select_team, select_operation)


def remove_participant(context):
    state = context.state
    save_prompt = f"Remove {state['participant_name']} from {state['team_name']}?"

    clear_cli()

    if is_confirmed := get_user_confirmation(save_prompt):
        setattr(state["participant"], "team_id", state["free_agent_team"].id)
        state["participant"].update()
        state["team_participants"].remove(state["participant"])

    render_result(
        state.get("participant_name"),
        OPS_CONFIG["remove_participant"].get("success_msg"),
        is_confirmed,
    )
    back_to_op_select(context, select_team, select_operation)


def delete_team(context):
    state = context.state
    team_name = state["team_name"]
    save_prompt = f"Permanently delete {state['team_name']}?"

    clear_cli()

    if is_confirmed := get_user_confirmation(save_prompt):
        for p in state["team_participants"]:
            setattr(p, "team_id", state["free_agent_team"].id)
            p.update()
        state["competing_teams"].remove(state["team"])
        state["team"].delete()
        state["team"] = None
        state["team_name"] = None
        state["team_participants"].clear()

    render_result(team_name, OPS_CONFIG["delete_team"].get("success_msg"), is_confirmed)
    context.restart()


def delete_participant(context):
    state = context.state
    participant_name = state["participant_name"]
    save_prompt = f"Permanently delete {state['participant_name']}?"

    clear_cli()

    if is_confirmed := get_user_confirmation(save_prompt):
        state["team_participants"].remove(state["participant"])
        state["participant"].delete()
        state["participant"] = None
        state["participant_name"] = None

    render_result(
        participant_name,
        OPS_CONFIG["delete_participant"].get("success_msg"),
        is_confirmed,
    )
    back_to_op_select(context, select_team, select_operation)


def update_participant_first_name(context):
    state = context.state
    config = OPS_CONFIG["update_participant_first_name"]
    render_header(
        config.get("title_suffix"),
        config.get("instruction"),
        state["participant_name"],
        state["team_name"],
        ctrl_c_cancel=True,
    )
    new_first_name = get_attr_value("participant", Participant.CONFIG.get("first_name"), USER_BACK)

    if new_first_name in sentinels:
        return resolve_nav_sentinel(
            new_first_name, context, back=USER_BACK, reset=USER_RESET, quit=USER_QUIT
        )

    save_prompt = f"Update first name to {generate_disp_text(new_first_name)}?"

    clear_cli()

    if is_confirmed := get_user_confirmation(save_prompt):
        setattr(state["participant"], "first_name", new_first_name)
        state["participant"].update()
        state["participant_name"] = generate_disp_text(state["participant"])
        state["team_participants"].sort(key=participant_sort)

    render_result(state["participant_name"], config.get("success_msg"), is_confirmed)
    back_to_op_select(context, select_team, select_operation)


def update_participant_last_name(context):
    state = context.state
    config = OPS_CONFIG["update_participant_last_name"]
    render_header(
        config.get("title_suffix"),
        config.get("instruction"),
        state["participant_name"],
        state["team_name"],
        ctrl_c_cancel=True,
    )
    new_last_name = get_attr_value("participant", Participant.CONFIG.get("last_name"), USER_BACK)

    if new_last_name in sentinels:
        return resolve_nav_sentinel(
            new_last_name, context, back=USER_BACK, reset=USER_RESET, quit=USER_QUIT
        )

    save_prompt = f"Update first name to {generate_disp_text(new_last_name)}?"

    clear_cli()

    if is_confirmed := get_user_confirmation(save_prompt):
        setattr(state["participant"], "last_name", new_last_name)
        state["participant"].update()
        state["participant_name"] = generate_disp_text(state["participant"])
        state["team_participants"].sort(key=participant_sort)

    render_result(state["participant_name"], config.get("success_msg"), is_confirmed)
    back_to_op_select(context, select_team, select_operation)


def update_team_name(context):
    state = context.state
    config = OPS_CONFIG["update_team_name"]
    render_header(
        config.get("title_suffix"),
        config.get("instruction"),
        team_name=state["team_name"],
        ctrl_c_cancel=True,
    )
    new_name = get_attr_value("team", Team.CONFIG.get("name"), USER_BACK)

    if new_name in sentinels:
        return resolve_nav_sentinel(
            new_name, context, back=USER_BACK, reset=USER_RESET, quit=USER_QUIT
        )

    save_prompt = f"Update team name to {generate_disp_text(new_name)}?"

    clear_cli()

    if is_confirmed := get_user_confirmation(save_prompt):
        setattr(state["team"], "name", new_name)
        state["team"].update()
        state["team_name"] = generate_disp_text(state["team"])
        state["competing_teams"].sort(key=team_sort)

    render_result(state["team_name"], config.get("success_msg"), is_confirmed)
    back_to_op_select(context, select_team, select_operation)


# set state object

initial_state = {
    "team": None,
    "team_name": None,
    "operation": None,
    "participant": None,
    "participant_name": None,
    "competing_teams": None,
    "free_agent_team": None,
    "team_participants": None,
    "free_agents": None,
    "save_prompt": None,
    "success_msg": None,
    "exec_func": None,
}

context = StepContext(select_team, initial_state)

# control flow

def main():
    while context.stack:
        step_func = context.stack[-1][0]
        step_state = context.stack[-1][1]
        context.state = step_state
        step_func(context)

    print(f"\n{generate_disp_text(EXIT_MSG, 'title')}\n")
    exit()

if __name__ == "__main__":
    main()