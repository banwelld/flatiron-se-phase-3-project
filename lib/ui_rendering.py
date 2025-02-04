from models.member import Member
from models.team import Team
import os
import time

# colour scheme

def title_str(text: str):
    return f"\x1b[38;2;0;253;255m{text}\x1b[0m"
    
def instruction_str(text: str):
    return f"\x1b[38;2;180;165;140m{text}\x1b[0m"
    
def success_str(text: str):
    return f"\x1b[38;2;102;204;0m{text}\x1b[0m"
    
def warning_str(text: str):
    return f"\x1b[38;2;255;220;0m{text}\x1b[0m"
    
def list_str(text: str):
    return f"\x1b[38;2;230;230;230m{text}\x1b[0m"
    
def back_str(text: str):
    return f"\x1b[38;2;255;147;0m{text}\x1b[0m"
    
def exit_str(text: str):
    return f"\x1b[38;2;255;70;95m{text}\x1b[0m"

def prompt_str(text: str):
    return f"\x1b[38;2;190;210;255m{text}\x1b[0m"

# exit program

def quit_program():
    os.system("clear")
    print(title_str("Good Bye!!"))
    exit()

#  menu schema

def generate_menu_schema(
    option_list: list, 
    menu_title: str, 
):
    """"
    Generates and returns a menu schema for either static or dynamic
    lists of menu items.
    """
    menu_items = option_list
    
    schema = {
        "menu_title": menu_title,
        "menu_items": menu_items,
    }
    
    return schema

# UI elements

def generate_menu(item_list: list, title: str):
    from helpers import handle_menu_input
    schema = generate_menu_schema(item_list, title)
    while True:
        render_menu_UI(schema['menu_title'], schema['menu_items'])
        exit_menu = handle_menu_input(schema['menu_title'], schema['menu_items'])
        if exit_menu:
            break

def render_menu_UI(title: str, options: dict):
        clear_current = "main menu" in title.lower()
        render_header(title, clear_current, clear_current)
        render_selection_options(options)
        render_alpha_options(title)
        print()
    
def render_input_UI(disp_name: str, class_type: type):
    render_header(
        f"{disp_name} {class_type.__name__.title()}",
        class_type == Team,          
        class_type == Member
    )
    print(instruction_str("Enter all requested information."))
    print()

def render_title(screen_title: str):
    os.system("clear")
    title_text = f"*** Trivia Team Tracker - {screen_title} ***"
    print(title_str(title_text.upper()))
    print(title_str("=" * len(title_text)))

def render_current_member():
    member = Member.get_current()
    if member is None:
        return
    print(member)
        
def render_current_team():
    team = Team.get_current()
    if team is None:
        return
    print(team)
            
def render_all_current():
    if Member.get_current() or Team.get_current():
        print(instruction_str(
            "Currently selected items:"))
        print()
        render_current_member()
        render_current_team()
        print()
        
def clear_all_current():
    Member.set_current(None)
    Team.set_current(None)

def render_header(
        title: str, clear_current_member: bool = False,
        clear_current_team: bool = False
):
    if clear_current_member:
        Member.set_current(None)
    if clear_current_team:
        Team.set_current(None)
    os.system("clear")
    render_title(title)
    print()
    render_all_current()

def render_selection_options(option_list: list):
    print(instruction_str("Select an option:"))
    print()
    for ind, row in enumerate(option_list, start=1):
        if type(row) == dict:
            print(list_str(f"{ind}: {row['option']}"))
        else:
            print(list_str(f"{ind}: {row}"))
    print()
    
def render_alpha_options(title: str):
    if Member.get_current() is not None or Team.get_current() is not None:
        print(warning_str("C: Clear selected options"))
    if "main menu" not in title.lower():
        print(back_str("B: Back to Previous Menu"))
    print(exit_str("X: Exit the Program"))

# display lists

def render_display_list(item_type: str, list_func: callable):
    render_header(f"{item_type.title()} Master List")
    for item in list_func():
        print(item)
    render_enter_to_continue()

# messages and warnings

def render_enter_to_continue():
    print()
    input(instruction_str("Hit <enter> to continue..."))
    
def render_success_message(item: object):
    os.system("clear")
    msg_header = success_str(f"{type(item).__name__} {item.id}")
    msg_content = list_str(f" : {item}")
    msg_orphaned_colon = list_str(" : ")
    msg_trailer = success_str("SUCCESS")
    print(f"{msg_header}{msg_content}{msg_orphaned_colon}{msg_trailer}")
    render_enter_to_continue()

def render_warning(warning_msg: str, seconds: int = 0):
    """
    Generates a blank screen with a warning message in red. The time
    parameter is required so that the function can determine whether to
    go back to the previous screen on timeout or to render a "press any
    key" message if the user selects 0 seconds.
    """
    os.system("clear")
    print(warning_str(warning_msg))
    if seconds > 0:
        time.sleep(seconds)
    else:
        render_enter_to_continue()
        
def warn_invalid_selection():
    render_warning("Invalid selection. Please try again.", 1.75)

def warn_invalid_char(display_name: str, char: str):
    render_warning(
        f"Invalid {display_name}: Includes the following: {char}.\n"
        "The only characters allowed in names are letters, period (.),\n"
        "apostrophe ('), or hyphen (-). Also, member names must not\n"
        "contain numerals (0 - 9).\n\n"
    )

def warn_length_invalid(disp_name: str, min_length: int, max_length: int):
    render_warning(
        f"Invalid {disp_name}: Length outside of expected range\n"
        f"({min_length} to {max_length} characters).\n\n"
    )

def warn_invalid_date_format(display_name: str):
    render_warning(
        f"Invalid {display_name}: Improper formatting.\n"
        "Expected date format is 'YYYY/MM/DD'.\n\n"
    )

def warn_date_invalid(display_name: str):
    render_warning(
        f"Invalid {display_name}: Date does not exist.\n"
        "Please check that day value is appropriate for the month\n"
        "and that the month value is between 1 and 12.\n\n"
    )
    
def warn_data_type_invalid(input_text: str, data_type: str):
    render_warning(
        f"'{input_text}' is wrong type for this operation: "
        f"Expected {data_type}.\n\n"
    )
    
def warn_no_such_item(class_type: type, search_by: str, input_text: str):
    render_warning(
        f"Cannot find {class_type.__name__.lower()} with "
        f"{search_by} {input_text}\n\n"
    )
    
def warn_no_team():
    render_warning("Current member is a free agent.\n\n")

def warn_already_member():
    render_warning("Member already belongs to the chosen team.\n\n")