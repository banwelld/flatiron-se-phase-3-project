import os
from typing import Union
from models.team.cls import Team
from models.participant.cls import Participant
from models.team.config import config as team_config
from models.participant.config import config as participant_config
from classes.session_state.cls import SessionState
from util.validation.warnings import (
    warn_invalid_selection,
    render_success_message,
)
from util.validation.frontend import is_valid_response
from util.validation.enforcers import (
    enforce_in_list,
    enforce_range,
    enforce_no_selection_overwrite,
)
from util.text_colour_map import text_colour_map as text_colour

# cancellation sentinel

USER_CANCELLATION = object()

# config maps

MODEL_CONFIG = {
    "participant": participant_config,
    "team": team_config,
}

OPERATIONS = {
    "select_operation": {
        "is_menu": True,
        "is_dependency": False,
        "is_pre_op": False,
        "nav_options": None,
        "display": {
            "title": "Operation Selection",
            "menu_text": None,
            "screen_prompt": "What operation would you like to perform?",
            "action_message": None,
        },
        "dependency_order": None,
        "action_func": lambda: handle_menu_operation("operation"),
    },
    "select_team": {
        "is_menu": True,
        "is_dependency": True,
        "is_pre_op": True,
        "nav_options": None,
        "display": {
            "title": "Team Selection",
            "menu_text": None,
            "screen_prompt": "What team would you like to work with?",
            "action_message": None,
        },
        "dependency_order": None,
        "action_func": lambda: handle_menu_operation("team"),
    },
    "select_participant": {
        "is_menu": True,
        "is_dependency": True,
        "is_pre_op": True,
        "nav_options": None,
        "display": {
            "title": "Participant Selection",
            "menu_text": None,
            "screen_prompt": "What participant would you like to work with?",
            "action_message": None,
        },
        "dependency_order": None,
        "action_func": lambda: handle_menu_operation("participant"),
    },
    "select_agent": {
        "is_menu": True,
        "is_dependency": True,
        "is_pre_op": True,
        "nav_options": None,
        "display": {
            "title": "Free Agent Selection",
            "menu_text": None,
            "screen_prompt": "What free agent would you like to work with?",
            "action_message": None,
        },
        "dependency_order": None,
        "action_func": lambda: handle_menu_operation("agent"),
    },
    "create_team": {
        "is_menu": False,
        "is_dependency": False,
        "is_pre_op": False,
        "nav_options": None,
        "display": {
            "title": "New Team",
            "menu_text": "Create a New Team",
            "screen_prompt": "Submit a response for each of the requested details.",
            "action_message": "Team created.",
        },
        "dependency_order": None,
        "action_func": lambda: create_entity_and_select("team"),
    },
    "create_participant": {
        "is_menu": False,
        "is_dependency": False,
        "is_pre_op": False,
        "nav_options": None,
        "display": {
            "title": "New Team Member",
            "menu_text": "Create a New Team Member",
            "screen_prompt": "Submit a response for each of the requested details.",
            "action_message": "Participant created.",
        },
        "dependency_order": {
            "select_team": 1,
            "select_agent": 0,
            "select_participant": 0,
            "assign_team_id": 2,
            "select_operation": 0,
        },
        "action_func": lambda: create_entity_and_select("participant"),
    },
    "add_free_agent_to_team": {
        "is_menu": False,
        "is_dependency": False,
        "is_pre_op": False,
        "nav_options": None,
        "display": {
            "title": "Add Free Agent",
            "menu_text": "Add Free Agent to Team",
            "screen_prompt": None,
            "action_message": "Participant added to team.",
        },
        "dependency_order": {
            "select_team": 1,
            "select_agent": 2,
            "select_participant": 0,
            "assign_team_id": 0,
            "select_operation": 0,
        },
        "action_func": lambda: add_free_agent_to_team(),
    },
    "assign_team_id": {
        "is_menu": False,
        "is_dependency": True,
        "is_pre_op": False,
        "nav_options": None,
        "display": None,
        "dependency_order": {
            "select_team": 1,
            "select_agent": 0,
            "select_participant": 2,
            "assign_team_id": 0,
            "select_operation": 0,
        },
        "action_func": lambda: assign_team_id(
            selected["participant"], selected["team"]
        ),
    },
    "remove_participant": {
        "is_menu": False,
        "is_dependency": False,
        "is_pre_op": False,
        "nav_options": None,
        "display": {
            "title": "Remove Participant",
            "menu_text": "Remove Participant from Team",
            "screen_prompt": None,
            "action_message": "Participant removed from team.",
        },
        "dependency_order": {
            "select_team": 1,
            "select_agent": 0,
            "select_participant": 2,
            "assign_team_id": 0,
            "select_operation": 0,
        },
        "action_func": lambda: remove_participant_from_team(),
    },
    "delete_participant": {
        "is_menu": False,
        "is_dependency": False,
        "is_pre_op": False,
        "nav_options": None,
        "display": {
            "title": "Delete Participant",
            "menu_text": "Delete Participant Record",
            "screen_prompt": None,
            "action_message": "Participant deleted.",
        },
        "dependency_order": {
            "select_team": 1,
            "select_agent": 0,
            "select_participant": 2,
            "assign_team_id": 0,
            "select_operation": 0,
        },
        "action_func": lambda: delete_entity("participant"),
    },
    "delete_team": {
        "is_menu": False,
        "is_dependency": False,
        "is_pre_op": False,
        "nav_options": None,
        "display": {
            "title": "Delete Team",
            "menu_text": "Delete Team Record",
            "screen_prompt": None,
            "action_message": "Team deleted - All participants made free agents.",
        },
        "dependency_order": {
            "select_team": 1,
            "select_agent": 0,
            "select_participant": 0,
            "assign_team_id": 0,
            "select_operation": 0,
        },
        "action_func": lambda: delete_entity("team"),
    },
    "update_participant_first_name": {
        "is_menu": False,
        "is_dependency": False,
        "is_pre_op": False,
        "nav_options": None,
        "display": {
            "title": "Update First Name",
            "menu_text": "Update Participant First Name",
            "screen_prompt": "Submit the participant's new first name.",
            "action_message": "Participant first name updated.",
        },
        "dependency_order": {
            "select_team": 1,
            "select_agent": 0,
            "select_participant": 2,
            "assign_team_id": 0,
            "select_operation": 3,
        },
        "action_func": lambda: update_entity_with_input(
            "participant",
            "first_name",
        ),
    },
    "update_participant_last_name": {
        "is_menu": False,
        "is_dependency": False,
        "is_pre_op": False,
        "nav_options": None,
        "display": {
            "title": "Update Last Name",
            "menu_text": "Update Participant Last Name",
            "screen_prompt": "Submit the participant's new last name.",
            "action_message": "Participant last name updated.",
        },
        "dependency_order": {
            "select_team": 1,
            "select_agent": 0,
            "select_participant": 2,
            "assign_team_id": 0,
            "select_operation": 3,
        },
        "action_func": lambda: update_entity_with_input(
            "participant",
            "last_name",
        ),
    },
    "update_team_name": {
        "is_menu": False,
        "is_dependency": False,
        "is_pre_op": False,
        "nav_options": None,
        "display": {
            "title": "Update Name",
            "menu_text": "Update Team Name",
            "screen_prompt": "Submit the team's new name.",
            "action_message": "Team name updated.",
        },
        "dependency_order": {
            "select_team": 1,
            "select_agent": 0,
            "select_participant": 0,
            "assign_team_id": 0,
            "select_operation": 0,
        },
        "action_func": lambda: update_entity_with_input("team", "name"),
    },
    "return_to_main": {
        "is_menu": False,
        "is_dependency": True,
        "is_pre_op": False,
        "nav_options": {
            "visibility": lambda open_menu_count: open_menu_count > 1,
            "format": "nope",
            "selectors": ("c",),
        },
        "display": {
            "title": None,
            "menu_text": "Clear All Selections and Return to Main Menu",
            "screen_prompt": None,
            "action_message": None,
        },
        "dependency_order": None,
        "action_func": lambda: return_to_main_menu(),
    },
    "quit_program": {
        "is_menu": False,
        "is_dependency": False,
        "is_pre_op": False,
        "nav_options": {
            "visibility": lambda open_menu_count: open_menu_count,
            "format": "angry",
            "selectors": ("x", "q"),
        },
        "display": {
            "title": "Exit Application",
            "menu_text": "Exit the Application",
            "screen_prompt": None,
            "action_message": None,
        },
        "dependency_order": None,
        "action_func": lambda: quit_program(),
    },
}

# validation collections

MENU_TYPES = tuple(
    key.replace("select_", "") for key, value in OPERATIONS.items() if value["is_menu"]
)

MODEL_NAMES = tuple(MODEL_CONFIG.keys())

# currently selected items

selected = {name: None for name in MODEL_NAMES}

# menu state

menu_reset = {item: False for item in MENU_TYPES}

open_menus = []

# operation handlers


def perform_operation(operation_name: str) -> Union[object, None]:
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

    enforce_in_list(operation_name, *OPERATIONS.keys())

    execution_order: tuple = generate_exec_order(operation_name)

    print(execution_order)

    for operation in execution_order:
        dependency = operation != operation_name
        result = run_exec_operation(operation, dependency)
        if result is USER_CANCELLATION:
            return USER_CANCELLATION


def run_exec_operation(operation: str, is_dependency: bool) -> None:
    if is_dependency:
        result = perform_operation(operation)
    else:
        result = OPERATIONS[operation]["action_func"]()

    return result


def create_entity_and_select(model_name: str) -> bool:
    """
    Creates a new entity instance of the specified model and adds it to the selected dict.
    Args:
        model_name (str): The name of the model to create an instance of.
                          Must be either 'participant' or 'team'.
    Returns:
        nothing (None): Nothing
    """
    enforce_in_list(model_name, *MODEL_NAMES)
    render_header(OPERATIONS[f"create_{model_name}"])

    model = Team if model_name == "team" else Participant
    required_attributes = generate_required_attribs_dict(model_name)
    attrib_values = collect_required_attrib_values(model_name, required_attributes)

    if attrib_values is USER_CANCELLATION:
        return USER_CANCELLATION

    entity_name = (
        attrib_values["name"]
        if model_name == "team"
        else format_participant_name(
            attrib_values["first_name"], attrib_values["last_name"]
        )
    )

    if not confirm_operation(f"Create {model_name} {entity_name}?"):
        return USER_CANCELLATION

    new_entity = model.create(**attrib_values)
    selected[model_name] = new_entity

    if model_name == "participant":
        success_screen_name = generate_participant_team_name_combo(
            entity_name, new_entity.team()
        )
    else:
        success_screen_name = generate_entity_display_name(new_entity)

    render_success_message(
        success_screen_name,
        OPERATIONS[f"create_{model_name}"]["display"]["action_message"],
    )


def update_entity_with_input(model_name: str, attrib_name: str) -> None:
    enforce_in_list(model_name, *MODEL_NAMES)
    render_header(OPERATIONS[f"update_{model_name}_{attrib_name}"])

    attrib_config = MODEL_CONFIG[model_name][attrib_name]
    new_attrib_value: str = get_validated_attrib_value(model_name, attrib_name)

    if new_attrib_value is USER_CANCELLATION:
        return USER_CANCELLATION

    if not confirm_operation(
        f"Update {model_name} {attrib_config['display_text']} to {new_attrib_value}?"
    ):
        return USER_CANCELLATION

    update_selected_entity_attrib(model_name, attrib_name, new_attrib_value)

    display_name = generate_entity_display_name(selected[model_name])
    render_success_message(
        display_name,
        OPERATIONS[f"update_{model_name}_{attrib_name}"]["display"]["action_message"],
    )


def assign_team_id(participant: Participant, team: Team):
    """
    Assigns a team ID to a participant and updates the participant. If
    no participant is provided, the selected participant will be used.
    If no team is provided, the selected team will be used. If the
    selected team's id attribute is the same as the participant's
    team_id attribute, the participant's team_id will be set to 0,
    indicating that the participant is a free agent

    Args:
        participant (Participant): The participant to whom the team ID will be
        assigned.
        team (Team): The team whose id is to be assigned to the participant.

    Returns:
        participant (Participant): The updated participant with the assigned team ID.
    """
    if participant is not None:
        setattr(participant, "team_id", team.id)
        participant.update()


def add_free_agent_to_team():
    """
    Adds a participant to a team. This function renders the header for the
    'add to team' operation and confirms the operation before assigning the
    team ID to the participant.
    """
    render_header(OPERATIONS["add_free_agent_to_team"])

    if not confirm_operation("Add the selected player to the selected team?"):
        return USER_CANCELLATION

    assign_team_id(selected["participant"], selected["team"])
    display_name = generate_entity_display_name(selected["participant"])
    render_success_message(
        display_name, OPERATIONS["add_free_agent_to_team"]["display"]["action_message"]
    )


def remove_participant_from_team():
    """
    Removes a participant from a team. This function renders the header for
    the 'remove from team' operation and confirms the operation before
    assigning the participant to the free-agent team.
    """
    render_header(OPERATIONS["remove_participant"])

    if not confirm_operation("Remove the selected player from their current team?"):
        return USER_CANCELLATION

    assign_team_id(selected["participant"], Team.all[0])
    display_name = generate_entity_display_name(selected["participant"])
    render_success_message(
        display_name, OPERATIONS["remove_participant"]["display"]["action_message"]
    )


def delete_entity(model_name: str):
    """
    Deletes the selected entity of the specified model type. Removes all
    participants from the team if the model type is 'team'.

    Args:
        model_name (str): The name of the model type to delete.
                          Must be either 'participant' or 'team'.

    Returns:
        nothing (None):
    """
    enforce_in_list(model_name, *MODEL_NAMES)
    render_header(OPERATIONS[f"delete_{model_name}"])

    if not confirm_operation(f"Delete the selected {model_name}?"):
        return USER_CANCELLATION

    # assigns all participants to the free-agent team
    if model_name == "team":
        depopulate_selected_team()

    display_name = generate_entity_display_name(selected[model_name])
    selected[model_name].delete()
    selected[model_name] = None
    render_success_message(
        display_name, OPERATIONS[f"delete_{model_name}"]["display"]["action_message"]
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
    enforce_in_list(option_type, *MENU_TYPES)
    if enforce_no_selection_overwrite(option_type, selected):
        return

    open_menus.append(option_type)

    options = get_menu_options(option_type)
    render_menu(option_type, options)
    selected_operation: str = get_operation_from_menu_response(options)
    result = perform_operation(selected_operation)

    open_menus.remove(option_type)

    return result


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
    enforce_in_list(option_type, *MENU_TYPES)

    if option_type == "participant":
        options = generate_participant_options()

    elif option_type == "agent":
        options = generate_free_agent_options()

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
        operation_name (str or None): The action function corresponding to the user's selection, or None if the selection is invalid.
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

    operation_name: str = get_nav_operation_name(user_input)
    return operation_name


# user operation aux functions


def update_selected_entity_attrib(model_name: str, attrib_name: str, new_value: str):
    """
    Updates the attribute of the selected entity with a new value.

    Args:
        model_name (str): The name of the model to update.
        attrib_name (str): The name of the attribute to update.
        new_value (str): The new value to set for the attribute.

    Returns:
        nothing (None):
    """
    entity = selected[model_name]
    setattr(entity, attrib_name, new_value)
    entity.update()


def generate_free_agent_options():
    return generate_participant_options(is_free_agent=True)


def generate_participant_options(is_free_agent: bool = False) -> tuple:
    """
    Generates a generator of participant options for a given team.

    Each option is a dictionary containing:
    - "menu_text": A string in the format "last_name, first_name" of the participant.
    - "selection_item": The participant object.

    Returns:
        options (tuple): A tuple of dictionaries with participant details.
    """
    option_source = (
        selected["team"].participants()
        if is_free_agent == False
        else Team.all[0].participants()
    )
    options = (
        {
            "menu_text": format_participant_name(
                participant.first_name,
                participant.last_name,
            ),
            "selection_item": participant,
            "operation_name": None,
        }
        for participant in option_source
        if selected["team"] is not None
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
        if team.id != 0
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
            "menu_text": attribs["display"].get(
                "menu_text", "** No Description Available **"
            ),
            "selection_item": None,
            "operation_name": operation_name,
        }
        for operation_name, attribs in OPERATIONS.items()
        if not attribs["is_menu"]
        and attribs["display"] is not None
        and attribs["nav_options"] is None
    )
    return options


def add_item_to_selected(selection_item: object):
    data_type = type(selection_item).__name__.lower()

    if data_type in MODEL_NAMES:
        selected[data_type] = selection_item


def validate_alpha_response(menu_response: str) -> bool:
    return any(
        (
            menu_response in val["nav_options"]["selectors"]
            for _, val in OPERATIONS.items()
            if val["nav_options"] is not None
            and val["nav_options"]["visibility"](len(open_menus))
        )
    )


def get_nav_operation_name(menu_response: str):
    return next(
        (
            operation_name
            for operation_name, attribs in OPERATIONS.items()
            if attribs["nav_options"] is not None
            and menu_response in attribs["nav_options"]["selectors"]
        ),
        None,
    )


def get_user_input_std(prompt_text: str) -> str:
    return input(text_colour["ask"](f"\n{prompt_text}"))


def prompt_for_attrib_value(model_name: str, attrib_display_text: str) -> str:
    try:
        prompt_text = f"{model_name.title()} {attrib_display_text}: "
        return get_user_input_std(prompt_text)
    except KeyboardInterrupt:
        return USER_CANCELLATION


def get_validated_attrib_value(model_name: str, attrib_name: str) -> str:
    while True:
        attrib_config = MODEL_CONFIG[model_name][attrib_name]
        response = prompt_for_attrib_value(model_name, attrib_config["display_text"])
        if response is USER_CANCELLATION:
            return USER_CANCELLATION
        if is_valid_response(attrib_config["display_text"], attrib_config, response):
            return response


def collect_required_attrib_values(model_name: str, required_attribs: dict) -> dict:
    user_response_collection = {}

    for attrib_name in required_attribs:
        response = get_validated_attrib_value(model_name, attrib_name)

        if response is USER_CANCELLATION:
            return USER_CANCELLATION

        user_response_collection[attrib_name] = response

    return user_response_collection


def generate_required_attribs_dict(model_name: str) -> dict:
    """
    Generates a dictionary of attributes necessary for the instantiation of a model.

    Args:
        model_name (str): The name of the model to generate required attributes for.

    Returns:
        required_attribs (dict): A dictionary containing the required attributes for
        the specified model.
    """
    required_attribs = {
        attrib_name: value
        for attrib_name, value in MODEL_CONFIG[model_name].items()
        if value["required"]
    }
    return required_attribs


# def get_operation_input(model_name: str, attrib_name: str):
#     prompt_text = f"{model_name.title()} {MODEL_CONFIG[model_name][attrib_name]['display_text']}: "
#     print()
#     return input(text_colour["ask"](prompt_text))


# def get_new_attrib_value(model_name: str, MODEL_CONFIG: dict, attrib_name: str):
#     valid_response = False
#     while not valid_response:
#         new_attrib_value = get_operation_input(model_name, attrib_name)
#         valid_response = is_valid_response(MODEL_CONFIG["display_text"], MODEL_CONFIG, new_attrib_value)
#     return new_attrib_value

# def collect_required_attrib_values(model_name: str) -> dict:
#     required_attribs = {
#         attrib_name: value for attrib_name, value
#         in MODEL_CONFIG[model_name].items()
#         if value["required"]
#     }
#     attrib_responses = {}

#     for attrib_name, value in required_attribs.items():
#         response = get_new_attrib_value(model_name, value, attrib_name)
#         if response == "!!":
#             return {}   # indicates that the user cancelled
#         attrib_responses[attrib_name] = response

#     return attrib_responses


def confirm_operation(confirmation_prompt: str):
    render_confirmation_prompt(confirmation_prompt)

    while True:
        response = input().lower()
        if response == "y":
            return True
        elif response == "n":
            return False
        else:
            print()
            print(
                text_colour["oops"](
                    "Invalid input. Please enter 'Y' to confirm or 'N' to cancel:"
                )
            )


# nav operations


def return_to_main_menu():
    clear_selected_values()
    return USER_CANCELLATION


def quit_program():
    clear_selected_values()
    render_header(OPERATIONS["quit_program"])
    if confirm_operation("Exit the application?"):
        render_exit_salutation()
        exit()


# UI rendering


def render_instruction(instruction: str):
    print()
    print(text_colour["plain"](instruction))
    print()


def render_title(text: str = ""):
    title = assemble_title(text)
    print(text_colour["title"](title.upper()))
    print(text_colour["title"]("=" * len(title)))


def render_selected_entities_table():
    if selected["participant"]:
        participant_info = generate_participant_team_name_combo(
            generate_entity_display_name(selected["participant"]),
            selected["participant"].team(),
        )
    else:
        participant_info = generate_entity_display_name(selected["participant"])

    team_name = generate_entity_display_name(selected["team"])

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
    
{text_colour["prompt"]("CURRENTLY SELECTED")}
{line}
{text_colour["prompt"]("Participant:")}  {participant_info}
{line}
{text_colour["prompt"]("Team:")}         {team_name}
{line}

    """

    print(selected_table)


def render_header(operation: dict):
    os.system("clear")
    render_title(operation["display"]["title"])

    if any(selected.values()):
        render_selected_entities_table()
    prompt = operation["display"]["screen_prompt"]
    if prompt is not None:
        render_instruction(prompt)


def render_menu_options(options: Union[tuple, dict, list]):
    for index, option in enumerate(options, start=1):
        if type(option) == dict:
            print(text_colour["option"](f"{index:<2} {option['menu_text']}"))
        else:
            print(text_colour["option"](f"{index:<2} {option}"))
    print()


def render_nav_options():
    options = (
        operation
        for operation in OPERATIONS.values()
        if operation["nav_options"] is not None
        and operation["nav_options"]["visibility"](len(open_menus))
    )

    for option in options:
        option_text = f"{option['nav_options']['selectors'][0].upper():<2} {option['display']['menu_text']}"
        print(text_colour[option["nav_options"]["format"]](option_text))

    print()


def render_menu(option_type: dict, options: tuple):
    render_header(OPERATIONS[f"select_{option_type}"])
    render_menu_options(options)
    render_nav_options()


def render_confirmation_prompt(confirmation_prompt: str):
    print()
    print()
    print(text_colour["oops"](confirmation_prompt))
    print()
    render_instruction("Enter 'Y' to condirm or 'N' to cancel:")


def render_exit_salutation():
    print()
    print(text_colour["fresh"]("Goodbye!"))
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
    deps = OPERATIONS[operation_name]["dependency_order"]

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
        if OPERATIONS[key]["is_dependency"] and OPERATIONS[key]["is_pre_op"]
    ]
    post_ops = [
        key
        for key in sorted_keys
        if OPERATIONS[key]["is_dependency"] and not OPERATIONS[key]["is_pre_op"]
    ]

    exec_order = tuple(pre_ops + [operation_name] + post_ops)
    return exec_order


def assemble_title(text: str) -> str:
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


def depopulate_selected_team():
    """
    Depopulates the selected team by assigning each member to the free-agent team.
    """
    if selected["team"] is not None:
        for participant in selected["team"].participants():
            assign_team_id(participant, Team.all[0])


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
    team_name_formatted = text_colour["nope"](team_name)
    open_paren = text_colour["fresh"]("(")
    close_paren = text_colour["fresh"](")")
    return f"{participant_name} {open_paren}{team_name_formatted}{close_paren}"


def generate_entity_display_name(
    entity: Union[Participant, Team, str, None] = None
) -> str:
    contextual_text_colour = "fresh"

    if isinstance(entity, Participant):
        entity_name = format_participant_name(entity.first_name, entity.last_name)
    elif isinstance(entity, Team):
        entity_name = entity.name
    elif isinstance(entity, str):
        entity_name = entity
    elif entity is None:
        entity_name = "None Selected"
        contextual_text_colour = "oops"

    return text_colour[contextual_text_colour](entity_name)


def get_greatest_participant_id() -> int:
    """
    Returns the ID of the participant with the greatest ID in Participant.all.
    """
    if not Participant.all:
        return None

    max_id = max(Participant.all.keys())

    return max_id


def delete_cancelled_participant() -> None:
    """
    Deletes a participant with the greatest participant ID if they are not assigned to any team.

    This function retrieves the participant with the greatest ID using the `get_greatest_participant_id` function.
    If no participant exists, the function returns early. If the participant exists but is not assigned to a team
    (i.e., their `team_id` is None), the .delete() method is run on the participant.

    Returns:
        None
    """
    if (target := get_greatest_participant_id()) is None:
        return
    if Participant.all[target].team_id is None:
        Participant.all[target].delete()


def clear_selected_values():
    for key in selected:
        selected[key] = None
