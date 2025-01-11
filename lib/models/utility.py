import re

class Utility:
    
    # validation methods
    
    @staticmethod
    def validate_int(*args):
        """Takes in any number of arguments and validates that they are all
        integers.
        """
        if not all(isinstance(arg, int) for arg in args):
            raise TypeError("All range validation arguments must be "
                            "integers.")
    
    
    def in_range(self, check_val: int, lower_lim: int, upper_lim: int):
        """Validates that the argument check_val lies within the range of the
        upper_lim and lower_lim arguments and throws value error if check_val
        is not within that range.
        """
        self.validate_all_integers(check_val, lower_lim, upper_lim)
        if not lower_lim <= check_val <= upper_lim:
            raise ValueError(f"Check value '{check_val}' is invalid, expected
                             integer between {lower_lim} and {upper_lim}")
    
    
    @staticmethod
    def valid_chars(check_val, regex: str):
        """Validates whether any part of the check_val argument matches
        the regex argument and throws value error if true."""
        if invalid_char := re.search(regex, check_val):
            raise ValueError(
                f"'{check_val}' contains invalid character "
                f"'{invalid_char.group()}', only letters, periods, hyphens, "
                f"apostrophes are allowed"
            )
            
