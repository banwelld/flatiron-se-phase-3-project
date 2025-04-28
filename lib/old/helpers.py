import os
from typing import Union, Type
from models.team import Team
from models.participant import Participant
from classes.session_state import SessionState
from config.old.operation_config import CONFIG as OPS_CONFIG
from modules.warnings import (
    warn_invalid_selection,
    render_result_screen,
)
from modules.get_attr_value import (
    validate_attr_value_response as is_valid_response,
)
from util.validation.enforcers import (
    enforce_free_agent_team_id_1,
    enforce_in_list,
    enforce_range,
)
from config.old.text_color_map import text_color_map as text_color

# cancellation sentinel

USER_CANCELLATION = object()

# function mapping for primary operations

OPS_FUNCS = {
    "select_operation": lambda: handle_menu_operation("operation"),
    "select_team": lambda: handle_menu_operation("team"),
    "select_participant": lambda: handle_menu_operation("participant"),
    "select_agent": lambda: handle_menu_operation("agent"),
    "create_team": lambda: create_entity_and_select(Team),
    "create_participant": lambda: create_entity_and_select(Participant),
    "add_free_agent_to_team": lambda: add_free_agent_to_team(),
    "assign_team_id": lambda: assign_team_id(
        entities_selected.get("participant"), entities_selected.get("team")
    ),
    "remove_participant": lambda: remove_participant_from_team(),
    "delete_participant": lambda: delete_entity("participant"),
    "delete_team": lambda: delete_entity("team"),
    "update_participant_first_name": lambda: update_entity_with_input(
        Participant, "first_name"
    ),
    "update_participant_last_name": lambda: update_entity_with_input(
        Participant, "last_name"
    ),
    "update_team_name": lambda: update_entity_with_input(Team, "name"),
    "return_to_main": lambda: return_to_main_menu(),
    "quit_program": lambda: quit_program(),
}

# validation collections

MENU_TYPES = (
    key.replace("select_", "") for key, value in OPS_CONFIG.items() if value["is_menu"]
)

MODEL_TYPES = ("participant", "team")

# fetch all teams from database

Team.fetch_all()

# validate the free agent team's id

free_agent_team = next((team for team in Team.all if team.is_free_agents))

enforce_free_agent_team_id_1(free_agent_team)

# instantiate state classes

entities_selected = SessionState(**{model: None for model in MODEL_TYPES})
members_loaded_by_team = SessionState(**{str(team.id): False for team in Team.all})
menus_open = SessionState(**{menu: False for menu in MENU_TYPES})

# primary operations


def perform_operation(operation_name: str) -> Union[Type, None]:
    """
    Executes a series of operations based on the provided operation name.
    The function enforces that the operation_name is valid, sets the
    execution flow for the given operation, and then executes each
    operation in the flow by calling the corresponding action function.

    Args:
        operation_name (str): The name of the operation to perform.

    Returns:
        completed (bool): True if the operation was completed successfully,
                          False otherwise. An incomplete operation indicates
                          that the user selected the "Return to main menu
                          and clear selected" option.
    """
    if operation_name is None:
        return

    enforce_in_list(operation_name, *OPS_CONFIG.keys())

    execution_order: tuple = generate_exec_order(operation_name)

    for operation in execution_order:
        dependency = operation != operation_name
        result = run_exec_operation(operation, dependency)
        if result is USER_CANCELLATION:
            return USER_CANCELLATION


def create_entity_and_select(model: Union[Participant, Team]) -> object:
    """
    Creates a new entity instance of the specified model and adds it to the selected dict.
    Args:
        model (Union[Participant, Team]): The model to create an instance of.
                                          Must be either 'Participant' or 'Team'.
    Returns:
        nothing (None): Nothing
    """
    model_type = get_model_type(model)

    enforce_in_list(model_type, *MODEL_TYPES)
    render_header(OPS_CONFIG[f"create_{model_type}"])

    required_attrs = generate_required_attrs_dict(model)
    attr_values = collect_required_attr_values(model, required_attrs)

    if attr_values is USER_CANCELLATION:
        return USER_CANCELLATION

    entity_name = (
        attr_values["name"]
        if model is Team
        else format_participant_name(
            attr_values["first_name"], attr_values["last_name"]
        )
    )

    if not confirm_operation(f"Create {model_type} {entity_name}?"):
        return USER_CANCELLATION

    new_entity = model.create(**attr_values)
    entities_selected.set(model_type, new_entity)

    if model is Participant:
        success_screen_name = generate_participant_team_name_combo(
            entity_name, new_entity.team()
        )
    else:
        success_screen_name = generate_entity_display_name(new_entity)

    render_result_screen(
        success_screen_name,
        OPS_CONFIG[f"create_{model_type}"]["display"]["action_message"],
    )


def update_entity_with_input(model: Union[Participant, Team], attr_name: str) -> object:
    model_type = get_model_type(model)

    enforce_in_list(model_type, *MODEL_TYPES)
    render_header(OPS_CONFIG[f"update_{model_type}_{attr_name}"])

    attr_config = model.CONFIG[attr_name]
    new_attr_value: str = get_validated_attr_value(model, attr_name)

    if new_attr_value is USER_CANCELLATION:
        return USER_CANCELLATION

    if not confirm_operation(
        f"Update {model_type} {attr_config['display_text']} to {new_attr_value}?"
    ):
        return USER_CANCELLATION

    update_selected_entity_attrib(model_type, attr_name, new_attr_value)

    display_name = generate_entity_display_name(entities_selected.get(model_type))
    render_result_screen(
        display_name,
        OPS_CONFIG[f"update_{model_type}_{attr_name}"]["display"]["action_message"],
    )


def assign_team_id(participant: Participant, team: Team):
    if participant is not None:
        setattr(participant, "team_id", team.id)
        participant.update()


def add_free_agent_to_team():
    """
    Adds a participant to a team. This function renders the header for the
    'add to team' operation and confirms the operation before assigning the
    team ID to the participant.
    """
    render_header(OPS_CONFIG["add_free_agent_to_team"])

    if not confirm_operation("Add the selected player to the selected team?"):
        return USER_CANCELLATION

    assign_team_id(entities_selected.get("participant"), entities_selected.get("team"))
    display_name = generate_entity_display_name(entities_selected.get("participant"))
    render_result_screen(
        display_name, OPS_CONFIG["add_free_agent_to_team"]["display"]["action_message"]
    )


def remove_participant_from_team():
    """
    Removes a participant from a team. This function renders the header for
    the 'remove from team' operation and confirms the operation before
    assigning the participant to the free-agent team.
    """
    render_header(OPS_CONFIG["remove_participant"])

    if not confirm_operation("Remove the selected player from their current team?"):
        return USER_CANCELLATION

    assign_team_id(entities_selected.get("participant"), Team.all[1])
    display_name = generate_entity_display_name(entities_selected.get("participant"))
    render_result_screen(
        display_name, OPS_CONFIG["remove_participant"]["display"]["action_message"]
    )


def delete_entity(model_type: str):
    """
    Deletes the selected entity of the specified model type. Removes all
    participants from the team if the model type is 'team'.

    Args:
        model_type (str): The name of the model type to delete.
                          Must be either 'participant' or 'team'.

    Returns:
        nothing (None):
    """
    enforce_in_list(model_type, *MODEL_TYPES)
    render_header(OPS_CONFIG[f"delete_{model_type}"])

    if not confirm_operation(f"Delete the selected {model_type}?"):
        return USER_CANCELLATION

    # assigns all participants to the free-agent team
    if model_type == "team":
        make_team_participants_free_agents(entities_selected.get(model_type).id)

    display_name = generate_entity_display_name(entities_selected.get(model_type))
    entities_selected.get(model_type).delete()
    entities_selected.set(model_type, None)
    render_result_screen(
        display_name, OPS_CONFIG[f"delete_{model_type}"]["display"]["action_message"]
    )


def handle_menu_operation(option_type: str):
    """
    Executes a menu operation based on the provided menu type.
    This function validates the given menu type, ensures no selection overwrite occurs,
    and manages the lifecycle of the menu operation. It opens the menu, renders it with
    the appropriate options, handles user input, and executes the corresponding action.
    Args:
        option_type (str): The type of menu to operate on. Must be a valid menu type.
    """
    menus_open.set(option_type, True)

    options = get_menu_options(option_type)
    render_menu(option_type, options)
    selected_operation: str = get_operation_from_menu_response(options)
    result = perform_operation(selected_operation)

    menus_open.set(option_type, False)

    return result


def return_to_main_menu():
    entities_selected.reset()
    return USER_CANCELLATION


def quit_program():
    entities_selected.reset()
    render_header(OPS_CONFIG["quit_program"])
    if confirm_operation("Exit the application?"):
        render_exit_salutation()
        exit()


# menu logic


def get_menu_options(option_type: str) -> tuple:
    """
    Generates and returns a tuple of menu options based on the provided option type.

    Args:
        option_type (str): The type of menu options to generate.
                           Must be one of 'participant', 'team', or 'operation'.

    Returns:
        options (tuple): A tuple containing the generated menu options.
    """
    if option_type == "participant":
        options = generate_participant_options()

    elif option_type == "agent":
        options = generate_participant_options(is_free_agent=True)

    elif option_type == "team":
        options = generate_team_options()

    elif option_type == "operation":
        options = generate_operation_options()

    return tuple(options)


def get_operation_from_menu_response(options: tuple) -> str:
    """
    Handles the user input for menu selection.

    Args:
        options (tuple): A tuple containing the menu options.

    Returns:
        operation_name (str or None): The action function corresponding
        to the user's selection, or None if the selection is invalid.
    """
    operation_name: str = None
    close_menu: bool = False

    while not close_menu:
        response = get_user_input_std("Enter your selection: ")

        if response.lstrip("-").isdigit():  # Strip leading '-' to handle negative
            operation_name = process_numeric_response(options, int(response))
            close_menu = (
                is_only_entities(options) and operation_name is None
            ) or operation_name is not None

        elif isinstance(response, str):
            operation_name = process_alpha_response(response)
            close_menu = operation_name is not None

        else:
            warn_invalid_selection()

    return operation_name


def process_numeric_response(options: tuple, menu_response: int) -> str:
    """
    Validates if the user's selection is one of the available options
    and, if so, invokes the selection's action attribute (always a
    function). If the option is a participant or team instance, adds the
    instance to its class' respective _current attribute so that it can
    be accessed in subsequent menus. If the user's selection is invalid,
    informs the user.

    Args:
        options (tuple): A tuple of menu options to validate the user's selection
        against.
        user_input (int): The user's selection.

    Returns:
        operation_name (str): The operation name of user's selection, or None if
        the selection is invalid.
    """
    try:
        enforce_range(menu_response, 1, len(list(options)))
        selection = options[menu_response - 1]

        if is_only_entities(options):
            add_item_to_selected(selection["selection_item"])

        return selection.get("operation_name")

    except ValueError:
        warn_invalid_selection()
        return None


def process_alpha_response(user_input: str) -> str:
    """
    Processes the user's alphabetic input and returns the corresponding operation name.

    Args:
        user_input (str): The alphanumeric input provided by the user.

    Returns:
        operation_name (str): The name of the operation corresponding to the user's input.
    """
    if not validate_alpha_response(user_input):
        return None

    return get_nav_operation_name(user_input)


# operation aux functions


def run_exec_operation(operation: str, is_dependency: bool) -> None:
    if is_dependency:
        result = perform_operation(operation)
    else:
        result = OPS_FUNCS[operation]()

    return result


def update_selected_entity_attrib(model_type: str, attr_name: str, new_value: str):
    """
    Updates the attribute of the selected entity with a new value.

    Args:
        model_type (str): The name of the model to update.
        attr_name (str): The name of the attribute to update.
        new_value (str): The new value to set for the attribute.

    Returns:
        nothing (None):
    """
    entity = entities_selected.get(model_type)
    setattr(entity, attr_name, new_value)
    entity.update()


def generate_participant_options(is_free_agent: bool = False) -> tuple:
    """
    Generates a generator of participant options for a given team.

    Each option is a dictionary containing:
    - "menu_text": A string in the format "last_name, first_name" of the participant.
    - "selection_item": The participant object.

    Returns:
        options (tuple): A tuple of dictionaries with participant details.
    """
    team_id = 1 if is_free_agent else entities_selected.get("team").id

    options = (
        {
            "menu_text": format_participant_name(
                participant.first_name,
                participant.last_name,
            ),
            "selection_item": participant,
            "operation_name": None,
        }
        for participant in get_team_participants(team_id)
    )
    return options


def generate_team_options() -> list:
    options = [
        {
            "menu_text": team.name,
            "selection_item": team,
            "operation_name": None,
        }
        for team in (Team.all.values() if Team.all.values() else Team.fetch_all())
        if not team.is_free_agent
    ]
    return options


def generate_operation_options():
    """
    Generates a generator of operation options based on the provided operations dictionary.

    The function filters out operations that are marked as navigation, menu, or have a description.
    For each valid operation, it creates a dictionary containing:
        - "menu_text": The description of the operation, or "No Description Available" if not provided.
        - "selection_item": Always set to None.

    Returns:
        options (generator): A generator yielding dictionaries with operation details.
    """
    options = (
        {
            "menu_text": attrs["display"].get(
                "menu_text", "** No Description Available **"
            ),
            "selection_item": None,
            "operation_name": operation_name,
        }
        for operation_name, attrs in OPS_CONFIG.items()
        if not attrs["is_menu"]
        and attrs["display"] is not None
        and attrs["nav_options"] is None
    )
    return options


def add_item_to_selected(selection_item: Type):
    data_type = type(selection_item).__name__.lower()

    if data_type in MODEL_TYPES:
        entities_selected.set(data_type, selection_item)


def validate_alpha_response(menu_response: str) -> bool:
    return any(
        (
            menu_response in val["nav_options"]["selectors"]
            for _, val in OPS_CONFIG.items()
            if val["nav_options"] is not None
            and val["nav_options"]["visibility"](len(menus_open.values()))
        )
    )


def get_nav_operation_name(menu_response: str):
    return next(
        (
            operation_name
            for operation_name, attrs in OPS_CONFIG.items()
            if attrs["nav_options"] is not None
            and menu_response in attrs["nav_options"]["selectors"]
        ),
        None,
    )


def get_user_input_std(prompt_text: str) -> str:
    return input(text_color["ask"](f"\n{prompt_text}"))


def prompt_for_attr_value(
    model_type: str, attr_display_text: str
) -> Union[str, object]:
    try:
        prompt_text = f"{model_type.title()} {attr_display_text}: "
        return get_user_input_std(prompt_text)
    except KeyboardInterrupt:
        return USER_CANCELLATION


def get_validated_attr_value(
    model: Union[Participant, Team], attr_name: str
) -> Union[str, object]:
    model_type = get_model_type(model)

    while True:
        attr_config = model.CONFIG[attr_name]
        response = prompt_for_attr_value(model_type, attr_config["display_text"])
        if response is USER_CANCELLATION:
            return USER_CANCELLATION
        if is_valid_response(attr_config["display_text"], attr_config, response):
            return response


def collect_required_attr_values(
    model: Union[Participant, Team], required_attrs: dict
) -> Union[str, object]:
    user_response_collection = {}

    for attr_name in required_attrs:
        response = get_validated_attr_value(model, attr_name)

        if response is USER_CANCELLATION:
            return USER_CANCELLATION

        user_response_collection[attr_name] = response

    return user_response_collection


def generate_required_attrs_dict(model: Union[Participant, Team]) -> dict:
    """
    Generates a dictionary of attributes necessary for the instantiation of a model.

    Args:
        model_type (str): The name of the model to generate required attributes for.

    Returns:
        required_attrs (dict): A dictionary containing the required attributes for
        the specified model.
    """
    required_attrs = {
        attr_name: value
        for attr_name, value in model.CONFIG.items()
        if value["required"]
    }
    return required_attrs


def confirm_operation(confirmation_prompt: str):
    render_confirmation_prompt(confirmation_prompt)

    while True:
        response = input().lower()
        if response == "y":
            return True
        elif response == "n":
            return False
        else:
            print(text_color["oops"]("Invalid input. 'Y' to confirm or 'N' to cancel:"))
            print()


# UI rendering


def render_instruction(instruction: str):
    print(text_color["plain"](instruction))
    print()


def render_esc_instruction():
    print(text_color["nope"]("(Hit Ctrl-C to return to the main menu.)"))
    print()


def render_title(text: str = ""):
    title = generate_title(text)
    print(text_color["title"](title.upper()))
    print(text_color["title"]("=" * len(title)))
    print()


def render_selected_entities_table():
    if entities_selected.get("participant"):
        participant_info = generate_participant_team_name_combo(
            generate_entity_display_name(entities_selected.get("participant")),
            entities_selected.get("participant").team(),
        )
    else:
        participant_info = generate_entity_display_name(
            entities_selected.get("participant")
        )

    team_name = generate_entity_display_name(entities_selected.get("team"))

    # the lengths are adjusted (down 6 or 69) to remove the excess from non-visible ANSI characters
    # and to add enuough space for the 'participant:' header at the beginning of each line.
    participant_info_length = (
        len(participant_info) - 7
        if len(participant_info) < 84
        else len(participant_info) - 69
    )
    team_length = len(team_name) - 6
    line = "-" * max(participant_info_length, team_length)

    selected_table = f"""
    
{text_color["prompt"]("CURRENTLY SELECTED")}
{line}
{text_color["prompt"]("Participant:")}  {participant_info}
{line}
{text_color["prompt"]("Team:")}         {team_name}
{line}

    """

    print(selected_table)


def render_header(operation: dict):
    display = operation["display"]

    os.system("clear")

    render_title(display.get("title"))
    if any(entities_selected.data.values()):
        render_selected_entities_table()
    if prompt := display.get("screen_prompt"):
        render_instruction(prompt)
    if operation.get("has_ctrlc_escape"):
        render_esc_instruction()


def render_menu_options(options: Union[tuple, dict, list]):
    for index, option in enumerate(options, start=1):
        if type(option) == dict:
            print(text_color["option"](f"{index:<2} {option['menu_text']}"))
        else:
            print(text_color["option"](f"{index:<2} {option}"))
    print()


def render_nav_options():
    options = (
        operation
        for operation in OPS_CONFIG.values()
        if operation["nav_options"] is not None
        and operation["nav_options"]["visibility"](len(menus_open.values()))
    )

    for option in options:
        option_text = f"{option['nav_options']['selectors'][0].upper():<2} {option['display']['menu_text']}"
        print(text_color[option["nav_options"]["format"]](option_text))

    print()


def render_menu(option_type: dict, options: tuple):
    render_header(OPS_CONFIG[f"select_{option_type}"])
    render_menu_options(options)
    render_nav_options()


def render_confirmation_prompt(confirmation_prompt: str):
    print()
    print()
    print(text_color["oops"](confirmation_prompt))
    print()
    render_instruction("Enter 'Y' to condirm or 'N' to cancel:")


def render_exit_salutation():
    print()
    print(text_color["fresh"]("Goodbye!"))
    print()
    print()


# utility functions


def generate_exec_order(operation_name: str) -> list:
    """
    Generates a list of operations (dependencies and main operation) based upon the execution
    order in the operations map for the given operation.

    Args:
        operation_name (str): The name of the operation for which to generate the execution list.

    Returns:
        exec_order (tuple): An ordered tuple of operations to be executed.
    """
    deps = OPS_CONFIG[operation_name]["dependency_order"]

    if deps is None:
        return (operation_name,)

    sorted_keys = [
        key
        for key, _ in sorted(deps.items(), key=lambda item: item[1])
        if deps[key] > 0
    ]
    pre_ops = [
        key
        for key in sorted_keys
        if OPS_CONFIG[key]["is_dependency"] and OPS_CONFIG[key]["is_pre_op"]
    ]
    post_ops = [
        key
        for key in sorted_keys
        if OPS_CONFIG[key]["is_dependency"] and not OPS_CONFIG[key]["is_pre_op"]
    ]

    exec_order = tuple(pre_ops + [operation_name] + post_ops)
    return exec_order


def generate_title(text: str) -> str:
    """
    Assemble the title for the application from the details for the selected operation.

    Args:
        text (str): The text to be included in the title (may be empty).

    Returns:
        title (str): The full title string for the selected operation.
    """
    formatted_text = " " if not text else f" - {text} "
    title = f"*** Trivia Team Tracker{formatted_text}***"
    return title


def make_team_participants_free_agents(team_id: int):
    """
    Depopulates the selected team by asszigning each member to the free-agent team.
    """
    if entities_selected.get("team") is not None:
        for participant in get_team_participants(team_id):
            assign_team_id(participant, Team.all[1])


def is_only_entities(options: tuple) -> bool:
    """
    Checks if the provided options contain only entities (participants or teams).

    Args:
        options (tuple): A tuple of options to check.

    Returns:
        bool: True if only entities are present, False otherwise.
    """
    return (
        True
        if all(
            isinstance(option["selection_item"], (Participant, Team))
            for option in options
        )
        else False
    )


def format_participant_name(first_name: str, last_name: str) -> str:
    return f"{last_name.upper()}, {first_name}"


def generate_participant_team_name_combo(participant_name: str, team_name: str) -> str:
    """
    Creates a formatted display name for a participant, including their team name.

    Args:
        participant_name (str): The participant name to be formatted.
        team_name (str): The participant's team's name.

    Returns:
        display_name (str): The formatted display name for the participant.
    """
    if not team_name:
        return participant_name
    team_name_formatted = text_color["nope"](team_name)
    open_paren = text_color["fresh"]("(")
    close_paren = text_color["fresh"](")")
    return f"{participant_name} {open_paren}{team_name_formatted}{close_paren}"


def generate_entity_display_name(
    entity: Union[Participant, Team, str, None] = None
) -> str:
    contextual_text_color = "fresh"

    if isinstance(entity, Participant):
        entity_name = format_participant_name(entity.first_name, entity.last_name)
    elif isinstance(entity, Team):
        entity_name = entity.name
    elif isinstance(entity, str):
        entity_name = entity
    elif entity is None:
        entity_name = "None Selected"
        contextual_text_color = "oops"

    return text_color[contextual_text_color](entity_name)


def get_model_type(model: Union[Participant, Team]) -> str:
    return model.__name__.lower()


def get_loaded_team_participants(team_id: int) -> list:
    return [p for _, p in Participant.all.items() if p.team_id == team_id]


def fetch_team_participants(team_id: int) -> list:
    members_loaded_by_team.set(team_id, True)
    return Participant.fetch_all(team_id)


def get_team_participants(team_id: int) -> list:
    if members_loaded_by_team.get(team_id):
        return get_loaded_team_participants(team_id)
    else:
        return fetch_team_participants(team_id)
