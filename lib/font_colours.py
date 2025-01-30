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