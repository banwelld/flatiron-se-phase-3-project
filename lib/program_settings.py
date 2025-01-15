PROGRAM_SETTINGS = {
    "Team": {
        "member_limit": 5,
        "table_def": {
            "name": "teams",
            "columns" : {
                "id": "INTEGER PRIMARY KEY",
                "name": "TEXT",
                "captain_id": "INTEGER"
            },
            "f_keys": [
                "FOREIGN KEY (captain_id) REFERENCES members(id)"
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
                "team_id": "INTEGER"
            },
            "f_keys": [
                "FOREIGN KEY (team_id) REFERENCES teams(id)"
            ]
        },
    }
}