from models.member import Member
from models.team import Team
from helpers import (
    render_title,
    render_working_with,
    warn_invalid_selection,
    get_input,
    quit_program,
    print_instr,
    print_list,
    print_back,
    print_exit,
)

# menu schema to create menus from static or dynamic lists
    
def menu_schema(
    option_list: list, 
    title: str, 
    action: callable
):
    """"
    Generates and returns a menu schema for either static or dynamic
    lists of menu items.
    """
    menu_items = option_list
    
    if action:
        menu_items = [
            {
                "option": item, 
                "action": action,
                "needs_member": [True, False],
                "needs_team": [True, False],
            }
            for item in option_list
        ]
    
    schema = {
        "menu_title": title,
        "menu_items": menu_items,
    }
    
    return schema

# dynamic menu interface

def menu_interface(menu_schema: dict):
    if menu_schema["menu_title"] == "Trivia League Main Menu":
        Member.set_current(None)
        Team.set_current(None)
    
    close_menu = False
    
    while not close_menu:
        title = menu_schema["menu_title"]
        options = menu_schema["menu_items"]
        
        render_title(title)
        render_working_with()
        render_menu_items(options)
        render_nav_options(title)
        
        selection = get_input("Enter your selection :: ", True)
        
        try:
            handle_integer_input(
                options, int(selection))
            
        except ValueError:
            print("WHY?????????????????????????????")
            get_input("click <enter>/", 0)
            close_menu = handle_alpha_input(
                selection, title)
        
def render_menu(item_list: list, title: str, action: callable = None):
    menu_interface(menu_schema(item_list, title, action))
        
# menu render assets

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

# input processing
  
def handle_integer_input(
    option_list: list[dict[str, any]],
    input_val: int,
):
    """
    Validates if the user's selection is one of the available options
    and, if so, invokes the selection's action attribute (always a 
    function). If the option is a member or team instance, adds the
    instance to its class' respective _current attribute so that it can
    be accessed in subsequent menus. If the user's selection is invalid,
    informs the user.
    """    
    if 1 <= input_val <= len(option_list):
        selection = option_list[input_val - 1]
        option = selection["option"]
        
        if isinstance(option, Member):
            Member.set_current(option)
        if isinstance(option, Team):
            Team.set_current(option)
        
        if selection["action"]:
            selection["action"]()
    
    else:
        warn_invalid_selection()
        
def handle_alpha_input(selection: str, title: str):
    if selection.lower() in ("x", "q"):
        quit_program()
    elif selection.lower() == "b" and title != "Trivia League Main Menu":
        return True
    elif selection == "":
        pass
    else:
        warn_invalid_selection()
        
    return False