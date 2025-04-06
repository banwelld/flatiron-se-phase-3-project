config = {
    "id": {
        "display_text": "ID",
        "help_text": None,
        "required": False,
        "validation": {},
    },
    "name": {
        "display_text": "name",
        "help_text": "No special characters",
        "required": True,
        "validation": {
            "validate_as": "name",
            "min_length": 5,
            "max_length": 30,
            "regex": r"[a-zA-Z0-9 '.\-]",
        },
    },
}
