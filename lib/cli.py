from colorama import Fore
import time
import os
from helpers import (
    quit_program
)

def main():
    while True:
        os.system("clear")
        print(Fore.RED + "*** TRIVIA LEAGUE TRACKER ***\n")
        main_menu()
        selection = input(Fore.LIGHTBLACK_EX + "\nEnter Selection : "
                          + Fore.RESET)
        if selection in ["Q", "q", "X", "x"]:
            os.system("clear")
            quit_program()
        
        elif selection == "1":
            while True:
                os.system("clear")
                print(Fore.RED + "*** MEMBER OPTIONS ***\n")
                member_options_menu()
                selection = input(Fore.LIGHTBLACK_EX + "\nEnter Selection : "
                                  + Fore.RESET)
                if selection in ["Q", "q", "X", "x"]:
                    os.system("clear")
                    quit_program()
                
                elif selection in ["B", "b"]:
                    break
                
                else:
                    os.system("clear")
                    print(Fore.RED + "Invalid selection. Please try again."
                          + Fore.RESET)
                    time.sleep(1.5)
        
        elif selection == "2":
            while True:
                os.system("clear")
                print(Fore.RED + "*** TEAM OPTIONS ***\n")
                team_options_menu()
                selection = input(Fore.LIGHTBLACK_EX + "\nEnter Selection : "
                                  + Fore.RESET)
                if selection in ["Q", "q", "X", "x"]:
                    os.system("clear")
                    quit_program()
                    
                elif selection in ["B", "b"]:
                    break
                
                else:
                    os.system("clear")
                    print(Fore.RED + "Invalid selection. Please try again."
                          + Fore.RESET)
                    time.sleep(1.5)
            
        else:
            os.system("clear")
            print(Fore.RED + "Invalid selection. Please try again."
                    + Fore.RESET)
            time.sleep(1.5)

def main_menu():
    print(Fore.LIGHTBLACK_EX + "Please select an option:\n")
    print(Fore.LIGHTCYAN_EX + "1. Member options")
    print("2. Team options")
    print(Fore.YELLOW + "\nX. Exit the program" + Fore.RESET)
    
def member_options_menu():
    print(Fore.LIGHTBLACK_EX + "Please select an option:\n")
    print(Fore.LIGHTCYAN_EX + "1. Browse all members")
    print("2. Add new member")
    print("3. Update member info")
    print("4. Delete a member")
    print(Fore.YELLOW + "\nB. Back to main menu")
    print("X. Exit the program" + Fore.RESET)
    
def team_options_menu():
    print(Fore.LIGHTBLACK_EX + "Please select an option:\n")
    print(Fore.LIGHTCYAN_EX + "1. Browse all teams")
    print("2. Add new team")
    print("3. Update team name")
    print("4. Delete a member")
    print(Fore.YELLOW + "\nB. Back to main menu")
    print("X. Exit the program" + Fore.RESET)

if __name__ == "__main__":
    main()