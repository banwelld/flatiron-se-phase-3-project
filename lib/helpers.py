from models.member import Member
from models.team import Team
from program_settings import PROGRAM_SETTINGS as ps
from datetime import datetime
import time
import os
import re

# print in colour

def print_title(text, sep=""):
    print(f"\033[38;2;0;253;255m{text}\033[0m", sep=sep)
    
def print_instr(text, sep=""):
    print(f"\033[38;2;160;160;160m{text}\033[0m", sep=sep)
    
def print_info(text, sep=""):
    print(f"\033[38;2;102;204;0m{text}\033[0m", sep=sep)
    
def print_warn(text, sep=""):
    print(f"\033[38;2;255;220;0m{text}\033[0m", sep=sep)
    
def print_list(text, sep=""):
    print(f"\033[38;2;250;250;250m{text}\033[0m", sep=sep)
    
def print_back(text, sep=""):
    print(f"\033[38;2;255;147;0m{text}\033[0m", sep=sep)
    
def print_exit(text, sep=""):
    print(f"\033[38;2;255;70;95m{text}\033[0m", sep=sep)

# exit program

def quit_program():
    os.system("clear")
    print_title("Good Bye!!")
    exit()

# display support functions

def render_title(title: str):
    os.system("clear")
    title_text = f"*** {title.upper()} ***"
    print_title(title_text)
    print_title("=" * len(title_text))
    print()

def render_current_member():
    member = Member._current
    if member is None:
        return
    
    team = Team.fetch_by_id(member.team_id)
    display_team = (
        "\033[38;2;255;220;0m * FREE AGENT *\033[0m"
        if team is None
        else team
    )
    print_info(
        f"{member.first_name} {member.last_name} : {member.birth_date} : "
        f"{display_team}"
    )
        
def render_current_team():
    team = Team._current
    if team is None:
        return
    
    captain = Team.fetch_by_id(team.captain_id)
    display_cpt = (
        "\033[38;2;255;220;0m * NO CAPTAIN *\033[0m"
        if captain is None
        else f"({captain}, team captain)"
    )
    print_info(f"{team.name} : {display_cpt}")
            
def render_working_with():
    if Member._current or Team._current:
        print_instr("Operations that you select will be performed on:")
        print()
        render_current_member()
        render_current_team()
        
def render_header(title: str):
    os.system("cls")
    render_title(title)
    render_working_with()
    
def render_success_message(item: Member | Team):
    print()
    succ_col = "\033[38;2;102;204;0m"
    reset = "\033[0m"
    print_list(
        f"{type(item).__name__} {item.id} : {item} : {succ_col}SUCCESS{reset}")
    get_input("Hit <enter> to continue",True)
    
def get_input(prompt: str, space_above=False):
    cr = "\n" if space_above else ""
    text_colour = "\033[38;2;160;160;160m"
    input_colour = "\033[38;2;250;250;250m"
    
    prompt_with_colour = f"{cr}{text_colour}{prompt}{input_colour}"
    selection = input(prompt_with_colour)
    
    return selection
    
def render_menu_items(option_list: list[dict[str, any]]):
    print_instr("Please select an option:")
    print()
    for ind, row in enumerate(option_list, start=1):
        print_list(f"{ind}: {row["option"]}")
    print()
    
def render_nav_options(title: str):
    if title != "Trivia League Main Menu":
        print_back("B: Back to Previous Menu")
    print_exit("X: Exit the Program")

def render_warning(warning_msg: str, seconds: int):
    """
    Generates a blank screen with a warning message in red. The time
    parameter is required so that the function can determine whether to
    go back to the previous screen on timeout or to render a "press any
    key" message if the user selects 0 seconds.
    """
    os.system("clear")
    print_warn(warning_msg)
    if seconds > 0:
        time.sleep(seconds)
    else:
        get_input("Hit <enter> to continue", True)
        
def warn_invalid_selection():
    render_warning("Invalid selection. Please try again.", 1.75)

def warn_invalid_char(display_name: str, char: str):
    message = (
        f"Invalid {display_name}: Includes the following: {char}.\n"
        "The only characters allowed in names are letters, period (.),\n"
        "apostrophe ('), or hyphen (-). Also, member names must not\n"
        "contain numerals (0 - 9)."
    )
    render_warning(message, 0)

def warn_attrib_length_invalid(
        display_name: str, 
        min_length: int, 
        max_length: int
):
    message = (
        f"Invalid {display_name}: Not within expected length parameters.\n"
        f"Expected length between {min_length} and {max_length} characters."
    )
    render_warning(message, 0)

def warn_invalid_date_format(display_name: str):
    message = (
        f"Invalid {display_name}: improper format.\n"
        "Expected date format is 'YYYY/MM/DD'."
    )
    render_warning(message, 0)

def warn_date_invalid(display_name: str):
    message = (
        f"Invalid {display_name}: Date does not exist.\n"
        "Please check that day value is appropriate for the month\n"
        "and that the month value is between 1 and 12."
    )
    render_warning(message, 0)

def attrib_length_valid(attribute: dict, check_val: str):
    min_length = attribute.get('min_length')
    max_length = attribute.get('max_length')

    if not min_length and not max_length:
        return True

    result = min_length <= len(check_val) <= max_length
    if not result:
        warn_attrib_length_invalid(attribute['disp_name'], min_length, max_length)

    return result

def attrib_chars_valid(attribute: dict, check_val: str):
    char_pattern = attribute.get('char_regex')
    
    if not char_pattern:
        return True

    if invalid_char := re.search(char_pattern, check_val):
        warn_invalid_char(attribute['disp_name'], invalid_char.group())

    return not bool(invalid_char)
    
def attrib_date_valid(attribute: dict, check_val: str, validate_function):
    if not attribute.get('valid_date_regex'):
        return True
    return validate_function(attribute, check_val)

def check_date_format(attribute: dict, check_val: str):
    date_regex = attribute.get('valid_date_regex')
    if result := bool(re.match(date_regex, check_val)):
        return result
    else:
        warn_invalid_date_format(attribute['disp_name'])
        return result

def check_date_value(attribute, check_val: str):
    try:
        return bool(datetime.strptime(check_val, "%Y/%m/%d"))
    except ValueError:
        warn_date_invalid(attribute['disp_name'])
        return False

def validated_user_input(attribute: dict, prompt: str):
    while True:
        input_val = input(prompt)
        if (
            attrib_length_valid(attribute, input_val)
            and attrib_chars_valid(attribute, input_val)
            and attrib_date_valid(attribute, input_val, check_date_format)
            and attrib_date_valid(attribute, input_val, check_date_value)
        ):
            return input_val

# creating and updating members/teams

def new_instance(class_type: type):
    params = {}
    attributes = {}
    
    for key, val in class_type.attrib_details.items():
        if "id" not in key:
            attributes[key] = val
    
    for attribute in attributes.keys():
        prompt = (
            f"Enter {class_type.__name__.lower()}'s "
            f"{attributes[attribute]['disp_name']}: "
        )
        
        params[attribute] = {
            attributes[attribute]['var_name']: validated_user_input(
                attributes[attribute],
                prompt
            )
        }

    return class_type.create(**params)

def update_attribute(class_type: type):
    attributes = {}
    
    print()
    if class_type.__name__.lower() == "member":
        print_instr("Hit <enter> with no text to skip any option.")
        print()
    
    for key, val in class_type.attrib_details.items():
        if "name" in key:
            attributes[key] = val
    
    for attribute in attributes:
        prompt = (
            f"Enter the {class_type.__name__.lower()}'s "
            f"{attributes[attribute]['disp_name']}: "
        )

        setattr(
            class_type._current,
            attribute['var_name'],
            validated_user_input(attribute, prompt)
        )
        
    return class_type._current.update()

def do_input_operation(input_function: callable, class_type: type):
    title = " ".join(input_function.__name__.split("_"))
    render_header(title)
    print_instr("Please enter the requested information:")
    print()
    
    item = input_function(class_type)
    if not item:
        return
    
    render_success_message(item)
    
def add_new_member():
    do_input_operation(new_instance, Member)
    
def add_new_team():
    do_input_operation(new_instance, Team)    
    
def update_name(obj: type, attribute: str):
    if obj.__name__.lower == "member":
        name = f"{Member._current.first_name} {Member._current.first_name}"
    else:
        name = Team._current.name
          
    do_input_operation(
        update_attribute(),
        obj,
        attrib=attribute, 
        prompt=(
            f"Please enter '{name}'s' new {' '.join(attribute.split('_'))}: ")
    )

def update_member_firstname():
    update_name(Member, "first_name")
    
def update_member_lastname():
    update_name(Member, "last_name")
    
def update_team_name():
    update_name(Team, "name")

def membership_change(operation: str):
    """
    Adds or removes a member from a team or elevates member to captain
    based on the operation parameter: "add" adds member, "remove"
    removes member, "add_captain" adds a captain, "remove_captain"
    removes a captain.
    """
    titles = {
        "add": "Assign Member to Team",
        "remove": "Remove Member from Team",
        "add_captain": "Assign Captain to Team",
        "remove_captain": "Remove Captain from Team",
    }
    title = titles.get(operation)
    
    if operation == "add_captain" and Member._current is None:
        select_member_from_roster()
    
    if operation == "add" and Team._current is None:
        select_team_from_roster()
        
    member = Member._current
    team = Team._current

    if operation == "remove" and member.team_id is None:
        return render_warning(
            f"{member} is a free agent and cannot be removed from a team.", 1.75
        )
    
    if operation == "remove_captain" and team.captain_id is None:
        return render_warning(
            f"Cannot remove {team}'s captain because the position is vacant.", 1.75
        )
    
    proceed = False
    while not proceed:
        print_operation = operation.replace("_", " ").title()
        render_header(title)
        print_warn(f"{team}: {print_operation} {member}?")
        
        choice = get_input("Enter 'Y' to confirm or 'N' to cancel: ", True).lower()
        if choice not in ("y", "n"):
            return warn_invalid_selection()
        elif choice == "n":
            return
        else:
            proceed = True

    if operation in ("add", "remove"):
        member.team_id = team.id if operation == "add" else None
        member.update()
    
    if operation in ("add_captain", "remove_captain"):
        team.captain_id = member.id if operation == "add_captain" else None
        team.update()

def assign_member_to_team():
    select_team_from_roster()
    if len(Member.fetch_all(team_id=Team._current.id)) >= ps.team.member_limit:
        return render_warning(
            "Team is at capacity. Either remove a member or try another team.",
            1.75
        )
    membership_change("add")
    
def remove_member_from_team():
    team = Team.fetch_by_id(Member.current.team_id)
    if team is None:
        return render_warning("Member is a free agent.", 1.75)
    membership_change("remove")
    
def assign_captain_to_team():
    team = Team._current
    select_member_from_roster(team_id=team.id)
    mem = Member._current
    if team.captain_id == mem.id:
        return render_warning("Member is the current team captain.", 1.75)
    if team.captain_id is not None and team.captain_id != mem.id:
        return render_warning(
            "Team already has a captain. Please remove "
            "prior to assigning a new captain.",
            1.75
        )
    membership_change("add_captain")
    
def remove_captain_to_team():
    member = Member.fetch_by_id(Team.current.captain_id)
    if member is None:
        return render_warning("Team captain position is already vacant.", 1.75)
    membership_change("remove_captain")
    
# searching for members and teams

def select_from_roster(obj: type, **kwargs):
    from dynamic_menu import render_menu
    obj_type = obj.__name__.title()
    roster = (obj.fetch_all() if not kwargs 
              else obj.fetch_all(**kwargs)
              )
    render_menu(roster, f"Select a {obj_type}")
    
def select_member_from_roster(**kwargs):
    select_from_roster(Member, **kwargs)

def select_team_from_roster(**kwargs):
    select_from_roster(Team, **kwargs)

def search_by_id(obj: Member | Team):
    render_header("Search by Name")
    obj_type = obj.__name__.lower()
    # try:
    id_number = int(get_input(
        f"Enter the {obj_type}'s ID number :: ",
        True
    ))
    item = obj.fetch_by_id(id_number)
    
    get_input(item, 0)
    
    if item:
        obj.set_current(item)
        render_success_message(item)
    else:
        render_warning(
            f"{obj_type.title()} with ID {id_number} not found.", 1.75)
    
    # except ValueError:
    #     render_warning("ID numbers must be integers.", 1)
        
def search_member_by_id():
    search_by_id(Member)
    
def search_team_by_id():
    search_by_id(Team)

def search_by_name(obj: type):
    render_header("Search by Name")
    obj_type = obj.__name__.lower()

    if obj_type == "member":
        params = {
            "first": get_input(f"Enter the {obj_type}'s first name :: ", True),
            "last": get_input(f"Enter the {obj_type}'s last name :: ")
        }
    else:
        params = {"name": get_input(f"Enter the {obj_type}'s name :: ", True)}
    
    result = obj.fetch_by_name(**params)
    
    obj.set_current(result)
    render_success_message(result)
    
def search_member_by_name():
    search_by_name(Member)
    
def search_team_by_name():
    search_by_name(Team)