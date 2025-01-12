from __init__ import CURSOR
from datetime import datetime
import re

class Utility:
    
    # validation methods
    
    @staticmethod
    def validate_int(*args):
        """Takes in any number of arguments and validates that they are all
        integers.
        """
        if not all(isinstance(arg, int) for arg in args):
            raise TypeError(
                "All range validation arguments must be integers.")
    
    @classmethod
    def check_in_range(cls, check_val: int, lower_lim: int, upper_lim: int):
        """Validates that the argument check_val lies within the range of the
        upper_lim and lower_lim arguments and throws value error if check_val
        is not within that range.
        """
        cls.validate_int(check_val, lower_lim, upper_lim)
        if not lower_lim <= check_val <= upper_lim:
            raise ValueError(
                f"Check value '{check_val}' is invalid, expected integer "
                f"between {lower_lim} and {upper_lim}")
    
    
    @staticmethod
    def check_valid_chars(check_val, regex: str):
        """Validates whether any part of the check_val argument matches
        the regex argument and throws value error if true."""
        if invalid_char := re.search(regex, check_val):
            raise ValueError(
                f"'{check_val}' contains invalid character "
                f"'{invalid_char.group()}', only letters, periods, hyphens, "
                f"apostrophes are allowed"
            )
            

    @staticmethod
    def check_date_format(check_val: str):
        """Validates that the supplied date string is formatted like
        'YYYY/MM/DD' and throws a value error if not."""
        valid_date = re.match(r"^[0-9]{4}(/[0-9]{2}){2}$", check_val)
        if not valid_date:
            raise ValueError(
                f"'{check_val}' format invalid, expected 'YYYY/MM/DD'")
            
    
    @staticmethod
    def check_valid_date(check_val: str):
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

    # Database interaction methods
    
    @staticmethod
    def fetch_db_row(table: str, **kwargs):
        """
        Execute SQL query to fetch a record from the specified table
        based on arguments for table and kwargs that houses column/criteria as
        key-value pairs. Throws ValueError if the table argument is not a valid
        table name or if kwargs is empty or TypeError for invalid kwargs values.
        """
        valid_tables = {"teams", "members"}
        if table not in valid_tables:
            raise ValueError(
                f"Invalid table name. Expected {valid_tables}, but got '{table}'"
            )
        if not kwargs:
            raise ValueError(
                "At least one column-value pair must be provided as search"
                "criteria"
            )
        
        conditions = []
        values = []
        
        for column, value in kwargs.items():
            if not isinstance(column, str):
                raise TypeError(
                    f"'{column}' invalid column name, expected string but got"
                    f"{type(column).__name__}."
                )
            conditions.append(f"{column} = ?")
            values.append(value)
        
        condition_clause = " AND ".join(conditions)
        sql = f"SELECT * FROM {table} WHERE {condition_clause}"
        
        data = CURSOR.execute(sql, tuple(values)).fetchone()
        return data