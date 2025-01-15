from datetime import datetime
import re

# validation

def check_is_integer(*args):
    """Takes in any number of arguments and validates that they are all
    integers.
    """
    if not all(isinstance(arg, int) for arg in args):
        raise TypeError(
            "All range validation arguments must be integers.")

def check_within_limits(check_val: int, lower_lim: int, upper_lim: int):
    """Validates that the argument check_val lies within the range of the
    upper_lim and lower_lim arguments.
    
    ValueError if check_val is not within that range.
    """
    check_is_integer(check_val, lower_lim, upper_lim)
    if not lower_lim <= check_val <= upper_lim:
        raise ValueError(
            f"Check value '{check_val}' is invalid, expected integer "
            f"between {lower_lim} and {upper_lim}")

def check_characters(check_val, regex: str):
    """Validates whether any part of the check_val argument matches
    the regex argument and throws value error if true."""
    if invalid_char := re.search(regex, check_val):
        raise ValueError(
            f"'{check_val}' contains invalid character "
            f"'{invalid_char.group()}', only letters, periods, hyphens, "
            f"apostrophes are allowed"
        )

def check_date_format(check_val: str):
    """Validates that the supplied date string is formatted like
    'YYYY/MM/DD' and throws a value error if not."""
    valid_date = re.match(r"^[0-9]{4}(/[0-9]{2}){2}$", check_val)
    if not valid_date:
        raise ValueError(
            f"'{check_val}' format invalid, expected 'YYYY/MM/DD'")

def check_date_value(check_val: str):
    """Separates the check_val string into month, date, and time for
    strings formatted like 'YYYY/MM/DD' and tries to turn it into a
    date using the date() method of timedate. If this generates a
    value error, a custom error message is passed.
    """        
    try:
        datetime.strptime(check_val, "%Y/%m/%d")
    except ValueError:
        raise ValueError(
            f"Date '{check_val}' invalid, check month/day combination")

# query constructor
    
def query_gen(
    operation: str,
    table_def: str,
    condition_cols: list[str] = [],
    assignment_cols: list[str] = []
):
    """
    Returns SQL generated according to the supplied arguments
    and table schemas dictated by the PS dictionary.
    
    Arguments:
        'operation': the sql verb, in lowercase, representing the
        type of query to be produced.
        
        'table_def': the name of the table definition found in the
        PS dictionary, which will be used in the creation
        of the query.
        
        'condition_cols': a list of all column names for which the
        query has conditions.
        
        'assignment_cols': a list of all column names for which the
        query has data to assign within the specified table.
        
        The table_def, all operations, and all column names are
        validated at the start of code execution. For 'insert' and
        'update' operations, assignment_cols is validated for
        truthiness. Execution will halt on ValueError if any value
        is not valid for the table specified in the table_def
        argument or if assignment_cols is falsey when operation is
        equal to 'insert' or 'update'.
    
    Operations:
        'create': creates a new database table based on the table
        definitions in the PS.
        
        'drop': deletes an existing table.
        
        'select': fetches all rows from the specified table,
        whether or not where conditions are supplied.
        
        'insert': adds a row to the specified table using the set
        conditions to supply the data.
        
        'update': changes one or more fields in the specified table
        for the row specified in the where conditions and values
        specified by the set conditions.
        
        'delete': deletes a row, based on the where conditions for
        the specified table.
    """
    
    # destructure table_def values to validate arguments

    table_name, columns, f_keys = table_def.values()
        
    valid_ops = ["create", "drop", "select", "insert", "update", "delete"]
    
    if not operation in valid_ops:
        raise ValueError(
            f"Invalid operation '{operation}', expected one of "
            f"{", ".join(valid_ops)}."
        )

    for item in condition_cols + assignment_cols:
        if item not in columns.keys():
            raise ValueError(
                f"Invalid column '{item}'. Column names must be in the "
                "PS columns dictionary for the specified table"
    )
    
    if operation in ("insert", "update") and assignment_cols is None:
        raise ValueError(
            "The assignment_cols argument is empty. Must have at least "
            f"one item to perform '{operation}' operation."
        ) 
            
    # SQL construction

    def where_clause():
        if not condition_cols:
            return ""
        conditions = [f"{col_name} = ?" for col_name in condition_cols]
        return f" WHERE {" AND ".join(conditions)}"
    
    if operation == "create":
        col_clauses = [f"{key} {value}" for key, value in columns.items()]
        col_schema = ", ".join(col_clauses + f_keys)
        return f"CREATE TABLE IF NOT EXISTS {table_name} ({col_schema})"
    
    if operation == "drop":
        return f"DROP TABLE IF EXISTS {table_name}"
    
    if operation == "select":
        return f"SELECT * FROM {table_name}" + where_clause()
        
    if operation == "delete":
        return f"DELETE FROM {table_name}" + where_clause()
    
    if operation == "update":
        param_list = [f"{col_name} = ?" for col_name in assignment_cols]
        params = ", ".join(param_list)
        return (
            f"UPDATE {table_name} SET {params}" + where_clause())

    if operation == "insert":
        col_count = len(assignment_cols)
        columns = ", ".join(assignment_cols)
        wildcards = ", ".join(["?"] * col_count)
        return (
            f"INSERT INTO {table_name} ({columns}) "
            f"VALUES ({wildcards})"
        )