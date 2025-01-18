from __init__ import CURSOR, CONN
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

def check_col_names(table_def, column_list):
    for column in column_list:
        if column not in table_def["columns"].keys():
            raise ValueError(
                f"'{column}' in criteria does not match any column name in "
                f"the '{table_def["name"]}' table schema."
            )

# database interaction

def create_table(table_def):
    columns = table_def["columns"]
    f_keys = table_def["f_keys"]
    
    col_clauses = [f"{key} {value}" for key, value in columns.items()]
    col_schema = ", ".join(col_clauses + f_keys)
    
    query = f"CREATE TABLE IF NOT EXISTS {table_def["name"]} ({col_schema})"
    CURSOR.execute(query)
    CONN.commit()
    
def drop_table(table_def):
    query = f"DROP TABLE IF EXISTS {table_def["name"]}"
    CURSOR.execute(query)
    CONN.commit()

def select_rows(table_def, **criteria):
    where_clause = ""
    col_names = criteria.keys()
    col_params = tuple(criteria.values())
    
    if criteria:
        check_col_names(table_def, col_names)
        where_clause = (
            f" WHERE " +
            " and ".join([f"{name} = ?" for name in col_names])
        )
        
    query = f"SELECT * FROM {table_def["name"]}" + where_clause
    return CURSOR.execute(query, col_params).fetchall()

def delete_row(table_def, id):
    query = f"DELETE FROM {table_def["name"]} WHERE id = {id}"
    CURSOR.execute(query)
    CONN.commit()

def write_data(table_def, id=None, **criteria):
    col_names = criteria.keys()
    col_values = tuple(criteria.values())

    check_col_names(table_def, col_names)
    
    if id:
        assignments = [f"{name} = ?" for name in col_names]
        assign_string = " and ".join(assignments)
        query = f"UPDATE {table_def["name"]} SET {assign_string} WHERE id = {id}"
    else:
        col_string = ", ".join(col_names)
        wild_string = ", ".join(["?"] * len(col_names))
        query = (
            f"INSERT INTO {table_def["name"]} ({col_string}) "
            f"VALUES ({wild_string})"
        )
    
    CURSOR.execute(query, col_values)
    CONN.commit()
    
    return None if id else CURSOR.lastrowid