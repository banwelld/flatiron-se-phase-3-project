from models.member import Member
from models.team import Team
from ui_rendering import (
    quit_program,
    instruction_str,
    prompt_str,
    render_display_list,
    render_input_UI,
    render_success_message,
    render_warning,
    generate_menu,
    warn_already_member,
    warn_date_invalid,
    warn_invalid_char,
    warn_invalid_date_format,
    warn_invalid_selection,
    warn_length_invalid,
    warn_no_such_item,
    warn_no_team,
    warn_team_full,
    warn_no_members,
)
from datetime import datetime
import os
import re

# menu interface logic

def handle_menu_input(title: str, options: dict):
    selection = input(instruction_str("Enter your selection: "))
    try:
        exit_menu = break_on_integer_input(options, int(selection))
        if "select" in title.lower():
            return exit_menu
        return False
    except ValueError:
        exit_menu = break_on_alpha_input(selection, title)
        if "main" not in title.lower():
            return exit_menu
        return False
  
def break_on_integer_input(option_list: list, input_val: int):
    """
    Validates if the user's selection is one of the available options
    and, if so, invokes the selection's action attribute (always a 
    function). If the option is a member or team instance, adds the
    instance to its class' respective _current attribute so that it can
    be accessed in subsequent menus. If the user's selection is invalid,
    informs the user.
    """    
    if 1 <= input_val <= len(option_list):
        option = option_list[input_val - 1]
        
        if isinstance(option, Member):
            Member.set_current(option)
        elif isinstance(option, Team):
            Team.set_current(option)
        elif type(option) == dict:
            opt_action = option.get('action')
            opt_action()
            return False
        else:
            raise TypeError(
                f"Option points to invalid item type. " 
                f"Expected Member, Team, Dict, but got {type(option)}"
            )
        return True
    else:
        warn_invalid_selection()
        return False
        
def break_on_alpha_input(selection: str, title: str):
    mem = Member.get_current()
    team = Team.get_current()
    if selection.lower() in ("x", "q"):
        quit_program()
    elif selection.lower() in ("b", "p") and "main menu" not in title.lower():
        return True
    elif selection.lower() == "c" and (mem is not None or team is not None):
        clear_both_current()
    elif selection == "":
        pass
    else:
        warn_invalid_selection()
    return False

# CLI operations and operation helper functions

CLI_user_input_ops = {
    "new": {
        "disp_name": "new",
        "action": lambda class_type, **params: class_type.create(**params),
        "success_msg": True,
    },
    "update": {
        "disp_name": "update",
        "action": (lambda class_type, **params: 
            full_attrib_update(class_type.get_current(), **params)),
    },
    "id_search": {
        "disp_name": "find",
        "action": (lambda class_type, **params: 
            class_type.set_current(class_type.fetch_by_id(**params))),
    },
    "name_search": {
        "disp_name": "find",
        "action": (lambda class_type, **params: 
            class_type.set_current(class_type.fetch_by_name(**params))),
    },
}

def get_user_input(class_type: type, attribute: dict):
    prompt_text = (f"Enter {class_type.__name__.lower()}'s "
                   f"{attribute['disp_name']}: ")
    input_text = input(prompt_str(prompt_text))
    print("INPUT: ", input_text)
    return input_text

def validated_input_text(operation: str, class_type: type, attribute: dict):
    max_attempts = 5
    disp_name = CLI_user_input_ops[operation]['disp_name']
    for attempt in range(1, max_attempts + 1):
        render_input_UI(disp_name, class_type)
        input_text = get_user_input(class_type, attribute)
        if input_is_valid(attribute, input_text):
            return input_text
    render_warning(
        "You have entered 5 invalid values in a row. "
        "Returning to main menu.",
        1.75
    ) 
    os.system("clear")
    return None

def full_attrib_update(item: object, **params):
    setattr(item, *params.values())
    return item.update()

def get_attribute_params(class_type: type, attributes: dict, operation: str):
    params = {}
    for attribute in attributes.keys():
        input_text = validated_input_text(
            operation,
            class_type,
            attributes[attribute]
        )
        if input_text is None:
            return None
        elif operation == "update":
            params['name'] = attributes[attribute]['attrib_name']
            params['value'] = input_text
        else:
            params[attribute] = input_text
    
    return params

def get_attributes(operation: str, class_type: type, attribute: str):
    if attribute is not None:
        return {attribute: class_type.attrib_details.get(attribute)}
    else:
        return {
            key:val for key, val in class_type.attrib_details.items()
            if operation in val['operations']
        }

def CLI_user_input_operation(operation: str, class_type: type, attribute: str = None):
    if operation == "update":
        ensure_current(class_type)
    attributes = get_attributes(operation, class_type, attribute)
    params = get_attribute_params(class_type, attributes, operation)
    if params is None:
        return None
    result = CLI_user_input_ops[operation]['action'](class_type, **params)
    
    if CLI_user_input_ops[operation]['disp_name'] in ("new", "update"):
        render_success_message(result)
    elif CLI_user_input_ops[operation] == "id_search":
        if result is None:
            warn_no_such_item(class_type, attribute, attributes.get(attribute))
            return
    elif CLI_user_input_ops[operation] == "name_search":
        if result is None:
            warn_no_such_item(
                class_type, "name", " ".join(attributes.values()).title())
            return
    else:
        pass
    
    return result

# member/team selection

def select_item_from_list(class_type: type):
    generate_menu(class_type.fetch_all(), f"{class_type.__name__.title()} Select")
    
def select_team_member(member_type: str):
    generate_menu(Team.get_current().list_members(), f"{member_type} Select")
    
def ensure_current(class_type: type):
    if class_type.get_current() is None:
        select_item_from_list(class_type)
        
def ensure_both_current():
    ensure_current(Member)
    if Member.get_current() is None:
        return
    ensure_current(Team)
    
def clear_current(class_type: type):
    if class_type.get_current() is not None:
        class_type.set_current(None)
        
def clear_both_current():
    clear_current(Member)
    clear_current(Team)
    
def update_current_member_team_id(new_value: int):
    mem = Member.get_current()
    mem.team_id = new_value
    mem.update()
    render_success_message(mem)
    
def assign_team_id_to_current_member():
    if not validate_add_member():
        return
    update_current_member_team_id(Team.get_current().id)
    clear_both_current()
        
def remove_team_id_from_current_member():
    if not validate_remove_member():
        return
    update_current_member_team_id(None)
    clear_both_current()
    
def update_current_team_captain_id(new_value: int):
    team = Team.get_current()
    team.captain_id = new_value
    team.update()
    render_success_message(team)
    
def assign_captain_id_to_current_team():
    if not validate_add_captain():
        return
    update_current_team_captain_id(Member.get_current().id)
    clear_both_current()
    
def reemove_captain_id_from_current_team():
    ensure_current(Team)
    if Team.get_current() is None:
        return
    update_current_team_captain_id(None)
    clear_both_current()
    
def delete_current_object(class_type: type):
    item = class_type.get_current()
    item.delete()
    render_warning("Item deleted successfully.", 0)
    
def delete_current_team():
    if not validate_delete_team():
        return
    delete_current_object(Team)
    clear_current(Team)
    
def delete_current_member():
    if not validate_remove_member():
        return
    delete_current_object(Member)
    clear_current(Member)
    
def update_captain_id(cpt_id: int):
    if Team.get_current() is not None:
        team = Team.get_current()
        team.captain_id = cpt_id
        team.update()
        render_success_message(team)
    
def delete_item(class_type: type):
    if class_type.get_current() is not None:
        item_name = class_type.get_current()._name
        class_type.get_current().delete()
        render_warning(f"{item_name} successfully deleted from application.", 0)
        
def show_active_team_roster():
    ensure_current(Team)
    team = Team.get_current()
    team_name = team.name.title()
    render_display_list(team_name, team.list_members)
    
# user input and operation validation

def name_is_valid(attribute: dict, check_val: str):
    return (
        string_length_ok(attribute, check_val)
        and string_chars_ok(attribute, check_val)
    )
    
def date_is_valid(attribute: dict, check_val: str):
    return (
        date_format_ok(attribute, check_val)
        and date_value_ok(attribute, check_val)
    )

def string_length_ok(attribute: dict, check_val: str):
    min_length = attribute.get('min_length')
    max_length = attribute.get('max_length')
    result = min_length <= len(check_val) <= max_length
    if not result:
        warn_length_invalid(attribute['disp_name'], min_length, max_length)
        
    return result

def string_chars_ok(attribute: dict, check_val: str):
    char_pattern = attribute.get('char_regex')
    if invalid_char := re.search(char_pattern, check_val):
        warn_invalid_char(attribute['disp_name'], invalid_char.group())
        return False
    return True

def date_format_ok(attribute: dict, check_val: str):
    date_pattern = attribute.get('date_regex')
    if not re.match(date_pattern, check_val):
        warn_invalid_date_format(attribute['disp_name'])
        return False
    return True

def date_value_ok(attribute: dict, check_val: str):
    try:
        datetime.strptime(check_val, "%Y/%m/%d")
        return True
    except ValueError:
        warn_date_invalid(attribute['disp_name'])
        return False

def input_is_valid(attribute: dict, input_text: str):
    if attribute['info_type'] == "date":
        validate_func = date_is_valid
    elif attribute['info_type'] == "name":
        validate_func = name_is_valid
    else:
        return True
    return validate_func(attribute, input_text)

def validate_membership():
    if Member.get_current() is None:
        return False
    if Member.get_current().team_id is None:
        warn_no_team()
        return False
    return True

def validate_is_member():
    if Member.get_current() is None or Team.get_current() is None:
        return False
    return Member.get_current().team_id == Team.get_current().id
    
def ensure_is_not_captain(team: type):
    if Member.get_current().id == team.captain_id:
        print()
        print("Member is captain of current teaam. Vacating team captain.")
        print()
        team.captain_id = None
        team.update()
        
def ensure_no_members():
    for mem in Team.get_current().list_members():
        print()
        print("Removing all members from team.")
        print()
        mem.team_id = None
        mem.update()
        
def ensure_team_has_capacity():
    if len(Team.get_current().list_members()) >= Team._MAX_CAPACITY:
        return False
    return True

def ensure_current_membership():
    if not len(Team.get_current().list_members()):
        return False
    return True

def validate_remove_member():
    ensure_current(Member)
    if Member.get_current() is None:
        return False
    if not validate_membership():
        return False
    ensure_is_not_captain(
        Team.fetch_by_id(
            Member.get_current().team_id
        )
    )
    return True

def validate_add_captain():
    ensure_current(Team)
    if not ensure_current_membership():
        warn_no_members()
        return False
    if Team.get_current() is None:
        return False
    select_team_member("captain")
    return True

def validate_delete_team():
    ensure_current(Team)
    if Team.get_current() is None:
        return False
    ensure_no_members()
    return True

def validate_add_member():
    ensure_both_current()
    if Team.get_current() is None or Member.get_current() is None:
        clear_both_current()
        return False
    if not ensure_team_has_capacity():
        warn_team_full()
        return False
    if validate_is_member():
        warn_already_member()
        return False
    if Member.get_current().team_id is not None:
        ensure_is_not_captain(Team.fetch_by_id(Member.get_current().team_id))
    return True