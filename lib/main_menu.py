from helpers import (
    render_header,
    print_list,
    print_exit,
    print_back,
    quit_program,
    get_input,
    warn_invalid_selection,
)

def main_menu():
    while True:
        render_header("Trivia Team Tracker - Main Menu")
        
        print_list("1. Member options")
        print_list("2. Team options")
        print()
        print_exit("X. Exit Trivia Team Tracker")
        
        choice = get_input("Enter your selection: ", True)
        
        if choice == "1":
            member_options_menu()
        elif choice == "2":
            team_options_menu()
        elif choice.lower() in ("x", "q"):
            quit_program()
        else:
            warn_invalid_selection()
            
def member_options_menu():
    proceed = False
    while proceed:
        render_header("Trivia Team Tracker - Member Options")
        
        print_list("1. Create member record")
        print_list("2. Find member by ID")
        print_list("3. Find member by name")
        print_list("4. Select member from member list")
        print_list("5. Update member name")
        print_list("6. Assign member to team")
        print_list("7. Remove member from team")
        print_list("8. Delete member record")
        print()
        print_back("B. Back to previous screen")
        print_exit("X. Exit Trivia Team Tracker")
        
        choice = get_input("Enter your selection", True)
        
        if choice == "1":
            
        elif choice == "2":
            
        elif choice == "3":
            
        elif choice == "4":
            
        elif choice == "5":
            
        elif choice == "6":
            
        elif choice == "7":
            
        elif choice == "8":
            
        elif choice.lower() in ("b", "p"):
            proceed = True
        elif choice.lower() in ("x", "q"):
            quit_program()
            