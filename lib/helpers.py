from models.member import Member
from models.team import Team
from menu_schemas.member_select import member_select
from colorama import Fore
import time
import os

# menu support functions

def quit_program():
    os.system("clear")
    print(
        Fore.MAGENTA + "\n*" + Fore.RED + "*" + Fore.YELLOW + "*" + 
        Fore.GREEN + " G" + Fore.CYAN + "O" + Fore.BLUE + "O" + 
        Fore.MAGENTA + "D " + Fore.LIGHTWHITE_EX + "B" + Fore.MAGENTA +
        "Y" + Fore.BLUE + "E" + Fore.CYAN + "!" + Fore.GREEN + "! " +
        Fore.YELLOW + "*" + Fore.RED + "*" + Fore.MAGENTA + "*" + 
        Fore.RESET + "\n"
    )
    exit()
    
def get_selection():
    print(Fore.LIGHTBLACK_EX)
    selection = input("Enter Selection : ")
    print(Fore.RESET)
    return selection

def inform_invalid_selection():
    os.system("clear")
    print(Fore.LIGHTRED_EX +
          "*** Invalid selection. Please try again. ***")
    print(Fore.RESET)
    time.sleep(1.75)

# functions for creating new members/teams with a combined UI
  
def create_new_member():
    first_name = input(Fore.LIGHTWHITE_EX + "First Name: ")
    last_name = input("Last Name: ")
    birth_date = input("Birth Date (YYYY/MM/DD): " + Fore.RESET)
    return Member.create(first_name, last_name, birth_date)

def create_new_team():
    team_name = input(Fore.LIGHTWHITE_EX + "Team Name: " + Fore.RESET)
    return Team.create(team_name)


def display_item_creation(class_type: str):
    from dynamic_menu import display_header
    display_header(f"Enroll New {class_type}")
    print(Fore.LIGHTBLACK_EX + 
          "Please enter the requested information:")
    print(Fore.RESET)
    
    try:
        new_item = (create_new_member() if class_type == "member" else
                    create_new_team())        
        
        print(Fore.LIGHTGREEN_EX)
        print(f"{class_type.capitalize()} {new_item.id} - "
            f"{new_item} - created successfully.")
        print(Fore.LIGHTBLACK_EX)
        input("Hit <enter> to continue" + Fore.RESET)
        
    except NameError:
        os.system("clear")
        print(Fore.RED +
              "Unable to complete the operation.\n"
              "The name contained invalid characters,\n" 
              "e.g., !, #, $, %, &."
              + Fore.RESET
        )
        print(Fore.LIGHTBLACK_EX)
        input("Hit <enter> to continue" + Fore.RESET)
        
    except ValueError:
        os.system("clear")
        print(Fore.RED + 
              "Unable to complete the operation.\n"
              "The name was not within the allowed\n"
              "length parameters:\n\n"
              "2 - 20 characters for first name\n"
              "2 - 30 for last name\n"
              "4 - 30 for team name\n"
              + Fore.RESET
        )
        print(Fore.LIGHTBLACK_EX)
        input("Hit <enter> to continue" + Fore.RESET)
        
    except RuntimeError:
        os.system("clear")
        print(Fore.RED + 
              "Unable to complete the operation.\n"
              "The date was formatted improperly or\n"
              "the date value was invalid."
              + Fore.RESET
        )
        print(Fore.LIGHTBLACK_EX)
        input("Hit <enter> to continue" + Fore.RESET)
        
# functions for finding a member or team
    
def seed_member_list():
    from dynamic_menu import dynamic_menu
    from menu_schemas.member_actions import member_actions
    member_select["menu_items"].clear()
    for member in Member.fetch_all():
        member_select["menu_items"].append(
            dict(option=member,
                 action=lambda: dynamic_menu(member_actions, member)))
        
def member_select_menu():
    from dynamic_menu import dynamic_menu
    seed_member_list()
    dynamic_menu(member_select)