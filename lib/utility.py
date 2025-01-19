from __init__ import CURSOR, CONN
from datetime import datetime
import re

# validation

def ensure_integers(*args):
    """
    Validates that all supplied arguments are integers.
    """
    if not all(isinstance(arg, int) for arg in args):
        raise TypeError("All supplied values must be integers.")

def enforce_range(check_val: int, lower_lim: int, upper_lim: int):
    """
    Validates that check_val lies within the inclusive range from
    lower_lim to upper_lim.

    Ensures that check_val is an integer. lower_lim and upper_lim are
    assumed to be hard-coded integers and are not validated.
    """
    ensure_integers(check_val)

    if not lower_lim <= check_val <= upper_lim:
        raise ValueError(
            f"'{check_val}' is out of range. Expected an integer between "
            f"{lower_lim} and {upper_lim}."
        )

def prevent_invalid_chars(check_val, regex: str):
    """
    Validates that check_val does not contain any characters that match
    the supplied regex pattern
    """
    if invalid_char := re.search(regex, check_val):
        raise ValueError(
            f"'{check_val}' contains an invalid character: "
            f"'{invalid_char.group()}'. Only letters, periods, hyphens, and"
            f"apostrophes are allowed"
        )

def enforce_date_format(check_val: str):
    """
    Ensures that check_val has valid date format (YYYY/MM/DD), with
    only digits 0 - 9 allowed in the year, month, day positions.
    """
    date_pattern = r"^[0-9]{4}(/[0-9]{2}){2}$"
    valid_date = re.match(date_pattern, check_val)
    if not valid_date:
        raise ValueError(
            f"'{check_val}' format invalid. expected 'YYYY/MM/DD' formatting"
            "with digits 0 - 9 in the Y, M, and D positions")

def validate_date(check_val: str):
    """
    Ensures that check_val has valid date formatting (YYYY/MM/DD) and then
    ensures that the date has a valid date value by attempting to apply the
    striptime() method of the datetime class.
    """
    enforce_date_format(check_val)
    
    try:
        datetime.strptime(check_val, "%Y/%m/%d")
    except ValueError:
        raise ValueError(
            f"Date '{check_val}' invalid, check month/day combination")
        
def ensure_valid_columns(table_def: dict, columns: list):
    for column in columns:
        if column not in table_def["columns"].keys():
            raise ValueError(
                f"'{column}' does not match any column name in the"
                f"'{table_def["name"]}' table schema."
            )

# database interaction

def create_table(table_def: dict):
    """
    Assembles and executes an SQL query that creates a table from data in the
    provided table definition and commits it to the connected database.
    """
    columns = [
        f"{name} {datatype}" for name, datatype in table_def["columns"].items()
    ]
    foreign_keys = table_def.get("foreign_keys", [])
    col_schema = ", ".join(columns + foreign_keys)
    
    query = f"CREATE TABLE IF NOT EXISTS {table_def['name']} ({col_schema})"
    CURSOR.execute(query)
    CONN.commit()
    
def drop_table(table_def: dict):
    """
    Assembles and executes an SQL query that drops the table specified in the 
    provided table definition and commits the change to the connected database.
    """
    query = f"DROP TABLE IF EXISTS {table_def["name"]}"
    CURSOR.execute(query)
    CONN.commit()

def select_rows(table_def: dict, **criteria: str):
    """
    Assembles and executes an SQL query that fetches all rows from the table
    specified in the provided table definition that match the provided
    criteria, if any, returning a list of all matching rows or an empty list
    if no rows matched.
    """
    conditions = []
    params = []

    for col, val in criteria.items():
        if val is None:
            conditions.append(f"{col} IS NULL")
        else:
            conditions.append(f"{col} = ?")
            params.append(val)

    where_clause = f" WHERE {' AND '.join(conditions)}" if conditions else ""
    query = (
        f"SELECT * "
        f"FROM {table_def['name']}"
        f"{where_clause}"
    )
    return CURSOR.execute(query, tuple(params)).fetchall()

def count_rows(table_def: dict, **criteria: str):
    """
    Assembles and executes an SQL query that counts all rows from the table
    specified in the provided table definition that match the provided
    criteria, if any. Filtering and grouping are applied to all provided
    criteria. Returns an integer representing the number of matching rows.
    """
    conditions = []
    params = []
        
    for col, val in criteria.items():
        if val is None:
            conditions.append(f"{col} IS NULL")
        else:
            conditions.append(f"{col} = ?")
            params.append(val)
    
    group_clause = (f" GROUP BY {', '.join(params)}" if params else "")
    where_clause = (
        f" WHERE {' AND '.join(conditions)}" if conditions else "")
    query = (
        f"SELECT COUNT(*) "
        f"FROM {table_def['name']}"
        f"{where_clause}"
        f"{group_clause}"
    )
    result = CURSOR.execute(query, params).fetchone()
    return result[0] if result else 0

def delete_row(table_def, id):
    """
    Assembles and executes an SQL query that deletes the table specified in the
    provided table definition and commits the change to the connected database.
    """
    query = (
        f"DELETE FROM {table_def["name"]} "
        f"WHERE id = {id}"
    )
    CURSOR.execute(query)
    CONN.commit()

def insert_row(table_def: dict, **criteria: str):
    """
    Assembles and executes an SQL query that inserts data, from the provided
    key/value criteria, into the table specified in the provided table
    definition and commits the change to the conected database.
    """
    columns = ", ".join(criteria.keys())
    wildcards = ", ".join(["?"] * len(criteria.keys()))
    query = (
        f"INSERT INTO {table_def["name"]} ({columns}) "
        f"VALUES ({wildcards})"
    )
    CURSOR.execute(query, tuple(criteria.values()))
    CONN.commit()
    return CURSOR.lastrowid

def update_row(table_def: dict, id: int = None, **updates: str):
    """
    Assembles and executes an SQL query that updates the data for a row in the
    table specified in the provided table definition and commits the change to
    the connected database. The query filters the table for a row matching the
    provided ID number and updates the fields in the columns matching the keys
    in the keyword criteria.
    """    
    assignment_string = ", ".join([f"{col} = ?" for col in updates.keys()])
    query = (
        f"UPDATE {table_def["name"]} "
        f"SET {assignment_string} "
        f"WHERE id = {id}")
    
    CURSOR.execute(query, tuple(updates.values()))
    CONN.commit()