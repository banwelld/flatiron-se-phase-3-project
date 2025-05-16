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
    resolve_sentinel,
)
from util.warnings import (
    warn_invalid_option,
)

# navigation sentinals

USER_BACK = object()
USER_RESET = object()
USER_QUIT = object()

sentinels = {
    "back": USER_BACK,
    "reset": USER_RESET,
    "quit": USER_QUIT,
}

# sort keys for participant and team lists

participant_sort = lambda p: (p.l_name, p.f_name)
team_sort = lambda t: t.name


# menu operations


def select_team(context):
    context.state["comp_teams"], context.state["free_team"] = fetch_teams()
    render_header(
        MENU_OPS_CONFIG["team"].get("title_suffix"),
        MENU_OPS_CONFIG["team"].get("instruction"),
        ctrl_c_cancel=False,
    )
    # create a list of tuples containing team names and objects
    team_options = [(t.name, t) for t in context.state["comp_teams"]]
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
    response = process_menu_response(menu_options, nav_options, **sentinels)

    if response in sentinels.values():
        return resolve_sentinel(response, context, **sentinels)

    elif isinstance(response, Team):
        context.state["team"] = response
        context.state["team_name"] = generate_disp_text(response)
        context.state["team_roster"] = Participant.fetch(context.state["team"].id)
        context.push(select_operation)

    elif isinstance(response, str):
        if not response in globals():
            warn_invalid_option()
            return context.restart()
        next_step_func = globals().get(response)
        context.push(next_step_func)


def select_operation(context):
    render_header(
        MENU_OPS_CONFIG["operation"].get("title_suffix"),
        MENU_OPS_CONFIG["operation"].get("instruction"),
        team_name=context.state["team_name"],
        team_roster=context.state["team_roster"],
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
        context.state["team"],
        len(context.state["team_roster"]),
        **sentinels,
    )
    if response in sentinels.values():
        return resolve_sentinel(response, context, **sentinels)

    context.state["operation"] = response
    next_step_func = (
        select_participant
        if OPS_CONFIG[response].get("resolve_participant")
        else globals().get(response)
    )
    context.push(next_step_func)


def select_participant(context):
    need_free_agents = OPS_CONFIG[context.state["operation"]]["load_free_agents"]
    render_header(
        OPS_CONFIG[context.state["operation"]].get("title_suffix"),
        MENU_OPS_CONFIG["participant"].get("instruction"),
        team_name=context.state["team_name"],
        team_roster=context.state["team_roster"] if need_free_agents else None,
        ctrl_c_cancel=False,
    )
    if need_free_agents:
        context.state["free_agents"] = context.state["free_team"].fetch_participants()

    participant_list = (
        context.state["free_agents"]
        if need_free_agents
        else context.state["team_roster"]
    )
    menu_options = tuple(
        (str(index), fmt_participant_name(p.f_name, p.l_name), p)
        for index, p in enumerate(participant_list, start=1)
    )
    nav_options = tuple(
        (op[0], attrs.get("menu_text"), op, attrs.get("format"))
        for op, attrs in NAV_OPS_CONFIG.items()
    )
    render_menu(menu_options, nav_options)
    response = process_menu_response(menu_options, nav_options, **sentinels)

    if response in sentinels.values():
        return resolve_sentinel(response, context, **sentinels)

    context.state["participant"] = response
    context.state["participant_name"] = generate_disp_text(response)
    op_func = globals().get(context.state["operation"])
    context.push(op_func)


# team and participant management operations


def create_team(context):
    op_config = OPS_CONFIG["create_team"]
    render_header(
        op_config.get("title_suffix"), op_config.get("instruction"), ctrl_c_cancel=True
    )
    team_name = get_attr_value("team", Team.CONFIG.get("name"), USER_BACK)

    if team_name in sentinels.values():
        resolve_sentinel(new_team, **sentinels)

    new_team = Team.create(team_name)
    save_prompt = f"Create team {generate_disp_text(new_team)}?"

    clear_cli()

    if is_confirmed := get_user_confirmation(save_prompt):
        new_team.save()
        context.state["team"] = new_team
        context.state["team_name"] = generate_disp_text(new_team)
        context.state["comp_teams"].append(new_team)
        context.state["comp_teams"].sort(key=team_sort)
        context.state["team_roster"] = []

    success_msg = f"{context.state['team_name']} : {op_config.get('success_msg')}"

    render_result(success_msg, is_confirmed)
    back_to_op_select(context, select_team, select_operation)


def create_participant(context):
    op_config = OPS_CONFIG["create_participant"]
    render_header(
        op_config.get("title_suffix"),
        op_config.get("instruction"),
        team_name=context.state["team_name"],
        team_roster=context.state["team_roster"],
        ctrl_c_cancel=True,
    )
    # organize the init attrs into a dict
    init_attr = {
        attr: attr_config
        for attr, attr_config in Participant.CONFIG.items()
        if attr_config.get("req_for_init")
    }
    # get values from the user for each attr
    user_attrs = {}
    for attr, attr_config in init_attr.items():
        user_attrs[attr] = get_attr_value("participant", attr_config, USER_BACK)

        if user_attrs[attr] in sentinels.values():
            return resolve_sentinel(user_attrs[attr], context, **sentinels)

    new_participant = Participant.create(**user_attrs)
    save_prompt = f"Create {generate_disp_text(new_participant)} and assign to {context.state['team_name']}?"

    clear_cli()

    if is_confirmed := get_user_confirmation(save_prompt):
        context.state["participant"] = new_participant
        setattr(context.state["participant"], "team_id", context.state["team"].id)
        new_participant.save()
        context.state["participant_name"] = generate_disp_text(
            context.state["participant"]
        )
        context.state["team_roster"].append(context.state["participant"])
        context.state["team_roster"].sort(key=participant_sort)

    success_msg = (
        f"{context.state['participant_name']} : {op_config.get('success_msg')}"
    )

    render_result(success_msg, is_confirmed)
    back_to_op_select(context, select_team, select_operation)


def recruit_free_agent(context):
    save_prompt = (
        f"Assign {context.state['participant_name']} to {context.state['team_name']}?"
    )

    clear_cli()

    if is_confirmed := get_user_confirmation(save_prompt):
        setattr(context.state["participant"], "team_id", context.state["team"].id)
        context.state["participant"].update()
        context.state["team_roster"].append(context.state["participant"])
        context.state["team_roster"].sort(key=participant_sort)

    success_msg = f"{context.state['participant_name']} : {OPS_CONFIG['recruit_free_agent'].get('success_msg')}"

    render_result(success_msg, is_confirmed)
    back_to_op_select(context, select_team, select_operation)


def remove_participant(context):
    save_prompt = (
        f"Remove {context.state['participant_name']} from {context.state['team_name']}?"
    )

    clear_cli()

    if is_confirmed := get_user_confirmation(save_prompt):
        setattr(context.state["participant"], "team_id", context.state["free_team"].id)
        context.state["participant"].update()
        context.state["team_roster"].remove(context.state["participant"])

    success_msg = f"{context.state['participant_name']} : {OPS_CONFIG['remove_participant'].get('success_msg')}"

    render_result(success_msg, is_confirmed)
    back_to_op_select(context, select_team, select_operation)


def del_team(context):
    save_prompt = f"Permanently delete {context.state['team_name']}?"
    success_msg = (
        f"{context.state['team_name']} : {OPS_CONFIG['del_team'].get('success_msg')}"
    )

    clear_cli()

    if is_confirmed := get_user_confirmation(save_prompt):
        # assign all participants to the free agent team
        for p in context.state["team_roster"]:
            setattr(p, "team_id", context.state["free_team"].id)
            p.update()
        context.state["comp_teams"].remove(context.state["team"])
        context.state["team"].delete()
        context.state["team"] = None
        context.state["team_name"] = None
        context.state["team_roster"].clear()

    render_result(success_msg, is_confirmed)
    if is_confirmed:
        context.restart()
    else:
        back_to_op_select(context, select_team, select_operation)


def del_participant(context):
    save_prompt = f"Permanently delete {context.state['participant_name']}?"
    success_msg = f"{context.state['participant_name']} : {OPS_CONFIG['del_participant'].get('success_msg')}"

    clear_cli()

    if is_confirmed := get_user_confirmation(save_prompt):
        context.state["team_roster"].remove(context.state["participant"])
        context.state["participant"].delete()
        context.state["participant"] = None
        context.state["participant_name"] = None

    render_result(success_msg, is_confirmed)
    back_to_op_select(context, select_team, select_operation)


def upd_participant_f_name(context):
    op_config = OPS_CONFIG["upd_participant_f_name"]
    render_header(
        op_config.get("title_suffix"),
        op_config.get("instruction"),
        context.state["participant_name"],
        context.state["team_name"],
        ctrl_c_cancel=True,
    )
    response = get_attr_value(
        "participant", Participant.CONFIG.get("f_name"), USER_BACK
    )

    if response in sentinels.values():
        return resolve_sentinel(response, context, **sentinels)

    save_prompt = f"Update first name to {generate_disp_text(response)}?"

    clear_cli()

    if is_confirmed := get_user_confirmation(save_prompt):
        setattr(context.state["participant"], "f_name", response)
        context.state["participant"].update()
        context.state["participant_name"] = generate_disp_text(
            context.state["participant"]
        )
        context.state["team_roster"].sort(key=participant_sort)

    success_msg = (
        f"{context.state['participant_name']} : {op_config.get('success_msg')}"
    )

    render_result(success_msg, is_confirmed)
    back_to_op_select(context, select_team, select_operation)


def upd_participant_l_name(context):
    op_config = OPS_CONFIG["upd_participant_l_name"]
    render_header(
        op_config.get("title_suffix"),
        op_config.get("instruction"),
        context.state["participant_name"],
        context.state["team_name"],
        ctrl_c_cancel=True,
    )
    resonse = get_attr_value("participant", Participant.CONFIG.get("l_name"), USER_BACK)

    if resonse in sentinels.values():
        return resolve_sentinel(resonse, context, **sentinels)

    save_prompt = f"Update last name to {generate_disp_text(resonse)}?"

    clear_cli()

    if is_confirmed := get_user_confirmation(save_prompt):
        setattr(context.state["participant"], "l_name", resonse)
        context.state["participant"].update()
        context.state["participant_name"] = generate_disp_text(
            context.state["participant"]
        )
        context.state["team_roster"].sort(key=participant_sort)

    success_msg = (
        f"{context.state['participant_name']} : {op_config.get('success_msg')}"
    )

    render_result(success_msg, is_confirmed)
    back_to_op_select(context, select_team, select_operation)


def upd_team_name(context):
    op_config = OPS_CONFIG["upd_team_name"]
    render_header(
        op_config.get("title_suffix"),
        op_config.get("instruction"),
        team_name=context.state["team_name"],
        ctrl_c_cancel=True,
    )
    response = get_attr_value("team", Team.CONFIG.get("name"), USER_BACK)

    if response in sentinels.values():
        return resolve_sentinel(response, context, **sentinels)

    save_prompt = f"Update team name to {generate_disp_text(response)}?"

    clear_cli()

    if is_confirmed := get_user_confirmation(save_prompt):
        setattr(context.state["team"], "name", response)
        context.state["team"].update()
        context.state["team_name"] = generate_disp_text(context.state["team"])
        context.state["comp_teams"].sort(key=team_sort)

    success_msg = f"{context.state['team_name']} : {op_config.get('success_msg')}"

    render_result(success_msg, is_confirmed)
    back_to_op_select(context, select_team, select_operation)


# set the step context for the CLI

initial_state = {
    "team": None,
    "team_name": None,
    "operation": None,
    "participant": None,
    "participant_name": None,
    "comp_teams": None,
    "free_team": None,
    "team_roster": None,
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


# entry point for the CLI
if __name__ == "__main__":
    main()
