PROGRAM_SETTINGS = {
    "Team": {
        "member_limit": 5,
        "table_def": {
            "name": "teams",
            "columns" : {
                "id": "INTEGER PRIMARY KEY",
                "name": "TEXT",
                "captain": "INTEGER"
            },
            "f_keys": [
                "FOREIGN KEY (captain) REFERENCES members(id)"
            ]
        }
    },
    "Member": {
        "table_def": {
            "name": "members",
            "columns" : {
                "id": "INTEGER PRIMARY KEY",
                "first_name": "TEXT",
                "last_name": "TEXT",
                "birth_date": "TEXT",
                "team": "INTEGER"
            },
            "foreign_keys": [
                "FOREIGN KEY (team) REFERENCES teams(id)"
            ]
        },
    }
}