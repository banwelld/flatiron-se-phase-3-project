from __init__ import CURSOR, CONN
from datetime import datetime
import re

# validation

def enforce_range(check_val: int, lower_lim: int, upper_lim: int):
    """
    Validates that check_val is an integer and lies within the inclusive
    range from lower_lim to upper_lim.
    """
    if not isinstance(check_val, int):
        raise TypeError("Invalid data type. Expected integer.")

    if not lower_lim <= check_val <= upper_lim:
        raise ValueError(f"'{check_val}' is out of range. Expected between "
                         f"{lower_lim} and {upper_lim}.")

def validate_chars(check_val, regex: str):
    """
    Validates that check_val does not contain any characters that match
    the supplied regex pattern
    """
    if invalid_char := re.search(regex, check_val):
        raise NameError(f"'{check_val}' contains an invalid character: "
                         f"'{invalid_char.group()}'.")

def enforce_date_format(check_val: str, regex: str):
    """
    Ensures that check_val has valid date format (YYYY/MM/DD), with
    only digits 0 - 9 allowed in the year, month, day positions.
    """
    date_regex = regex
    valid_date = re.match(date_regex, check_val)
    if not valid_date:
        raise RuntimeError(
            f"'{check_val}' format invalid. Expected 'YYYY/MM/DD'.")

def validate_date(check_val: str, regex: str):
    """
    Ensures that check_val has valid date formatting (YYYY/MM/DD) and
    then ensures that the date has a valid date value by attempting to
    apply the striptime() method of the datetime class.
    """
    enforce_date_format(check_val, regex)
    try:
        datetime.strptime(check_val, "%Y/%m/%d")
    except ValueError:
        raise RuntimeError(f"Date '{check_val}' invalid.")


# database interaction

def create_table(table_def: dict):
    """
    Assembles and executes an SQL query that creates a table from data
    in the provided table definition and commits it to the connected
    database.
    """
    columns = [f"{name} {datatype}" for name, datatype 
               in table_def["columns"].items()]
    
    foreign_keys = table_def.get("foreign_keys", [])
    col_schema = ", ".join(columns + foreign_keys)
    
    query = f"CREATE TABLE IF NOT EXISTS {table_def['name']} ({col_schema})"
    CURSOR.execute(query)
    CONN.commit()
    
def drop_table(table_def: dict):
    """
    Assembles and executes an SQL query that drops the table specified
    in the provided table definition and commits the change to the
    connected database.
    """
    query = f"DROP TABLE IF EXISTS {table_def['name']}"
    CURSOR.execute(query)
    CONN.commit()

def select_all_rows(table_def: dict):
    """
    Assembles and executes an SQL query that fetches all rows from the
    table specified in the provided table definition that match the
    provided criteria, if any, returning a list of all matching rows or
    an empty listif no rows matched.
    """     
    sort_clause = (
        f"ORDER BY {'name' if table_def['name'] == 'teams' else 'last_name'}")
    query = f"SELECT * FROM {table_def['name']} {sort_clause}"
    return CURSOR.execute(query).fetchall()

def select_one_row(table_def: dict, **kwargs):
    """
    Assebles and executes an SQL query that returns one record from the
    table specified in the the table_def argument. Accepts 2 arguments
    but returns results filtered for the first one with a value since
    this query's sole purpose is to search on one criterion.
    """
    if "id" in kwargs:
        where_clause = "WHERE id = ?"
        val = (kwargs["id"],)
    elif "name" in kwargs:
        where_clause = "WHERE name = ?"
        val = (kwargs["name"],)
    elif "first" in kwargs and "last" in kwargs:
        where_clause = "WHERE first_name = ? AND last_name = ?"
        val = (kwargs["first"], kwargs["last"])
    else:
        raise ValueError("No valid filtering criteria provided.")
    
    query = f"SELECT * FROM {table_def['name']} {where_clause}"
    return CURSOR.execute(query, val).fetchone()

def delete_row(table_def: dict, id: int):
    """
    Assembles and executes an SQL query that deletes the table specified
    in the provided table definition and commits the change to the
    connected database.
    """
    query = f"DELETE FROM {table_def['name']} WHERE id = ?"
    CURSOR.execute(query, (id,))
    CONN.commit()

def insert_row(table_def: dict, **criteria):
    """
    Assembles and executes an SQL query that inserts data, from the
    provided key/value criteria, into the table specified in the
    provided table definition and commits the change to the conected
    database.
    """
    columns = ", ".join(criteria.keys())
    wildcards = ", ".join(["?"] * len(criteria.keys()))
    
    query = f"INSERT INTO {table_def['name']} ({columns}) VALUES ({wildcards})"
    CURSOR.execute(query, tuple(criteria.values()))
    CONN.commit()
    
    return CURSOR.lastrowid

def update_row(table_def: dict, id: int, **updates):
    """
    Assembles and executes an SQL query that updates the data for a row
    in the table specified in the provided table definition and commits
    the change to the connected database. The query filters the table
    for a row matching the provided ID number and updates the fields in
    the columns matching the keys in the keyword criteria.
    """
    assignment_string = ", ".join([f"{col} = ?" for col in updates.keys()])
    where_clause = "WHERE id IS NULL" if id is None else "WHERE id = ?"
    assignment_values = [val for val in updates.values()]
    
    if id is not None:
        assignment_values.append(id)

    query = (f"UPDATE {table_def['name']} "
             f"SET {assignment_string} {where_clause}")
    
    CURSOR.execute(query, tuple(assignment_values))
    CONN.commit()