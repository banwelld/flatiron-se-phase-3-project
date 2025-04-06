config = {
    "id": {
        "display_text": "ID",
        "help_text": None,
        "required": False,
        "validation": {},
    },
    "first_name": {
        "display_text": "first name",
        "help_text": "No numeric or special characters",
        "required": True,
        "validation": {
            "validate_as": "name",
            "min_length": 2,
            "max_length": 20,
            "regex": r"[a-zA-Z '.\-]",
        },
    },
    "last_name": {
        "display_text": "last name",
        "help_text": "No numeric or special characters",
        "required": True,
        "validation": {
            "validate_as": "name",
            "min_length": 2,
            "max_length": 30,
            "regex": r"[a-zA-Z '.\-]",
        },
    },
    "birth_date": {
        "display_text": "birth date",
        "help_text": "YYYY-MM-DD expected",
        "required": True,
        "validation": {
            "validate_as": "date",
            "min_length": None,
            "max_length": None,
            "regex": r"^[0-9]{4}(-[0-9]{2}){2}$",
        },
    },
    "team_id": {
        "display_text": "ID",
        "help_text": None,
        "required": False,
        "validation": {},
    },
}
