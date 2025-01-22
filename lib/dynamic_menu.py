from models.member import Member
from models.team import Team
from colorama import Fore
import os
from helpers import (
    inform_invalid_selection,
    get_selection,
)

# dynamic menu

def dynamic_menu(
    data_source: dict, 
    member: Member = None, 
    team: Team = None
):
    go_back = False

    while not go_back:
        display_header(data_source["menu_title"])
        display_dynamic_options(data_source)
        
        selection = get_selection()
        
        try:
            handle_integer_input(data_source["menu_items"],
                                 int(selection))
        except ValueError:
            go_back = handle_string_input(data_source, selection)

# display components

def display_header(title: str):
    os.system("clear")
    title_text = f"*** {title.upper()} ***"
    print(Fore.BLUE + title_text)
    print("=" * len(title_text))
    print(Fore.RESET)

def dynamic_menu_options(option_list: list[dict[str, str]]):
    print(Fore.LIGHTBLACK_EX + 
          "Please select from these options:" + Fore.RESET)
    print(Fore.LIGHTWHITE_EX)
    for ind, row in enumerate(option_list, start=1):
        print(f"{ind}: {row["option"]}")
    print(Fore.RESET)
    
def dynamic_nav_options(option_list: list[dict[str, str]] = []):
    for row in option_list:
        menu_item = f"{row["selector"].upper()}: {row["option"]}"
        colour = (Fore.LIGHTRED_EX if row["selector"] == "x" 
                  else Fore.LIGHTYELLOW_EX)

        print(colour + menu_item + Fore.RESET)
        
def display_dynamic_options(
    data_source: dict[str, str | list[dict[str, str]]]):
    dynamic_menu_options(data_source["menu_items"])
    dynamic_nav_options(data_source["nav_options"])

# input processing
  
def handle_integer_input(
    option_list: list[dict[str, str]], input_val: int):
    # validate input between 1 and the length of the option list
    if 1 <= input_val <= len(option_list):
        # call the function associated with the menu item
        action = option_list[input_val - 1]["action"]
        action()
    else:
        inform_invalid_selection()

def handle_string_input(data_source, input_val: str):
    valid_chars = []
    
    # list all of the menu's valid string input values
    for option in data_source["nav_options"]:
        valid_chars.append(option["selector"])

    # validate the input valus
    if input_val.lower() in valid_chars:
        # find the action in the option's dictionary and run it
        [action] = [option["action"] for option in 
                    data_source["nav_options"] if 
                    option["selector"] == input_val.lower()] 
        if action is not None:
            action()
        else:
            return True
    else:
        inform_invalid_selection()