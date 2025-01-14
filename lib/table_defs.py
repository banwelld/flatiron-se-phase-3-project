TABLE_DEFS = {
    "member_table": {
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
    "team_table": {
        "name": "teams",
        "columns" : {
            "id": "INTEGER PRIMARY KEY",
            "name": "TEXT",
            "captain_id": "INTEGER",
            "member_cap": "INTEGER"
        },
        "f_keys": [
            "FOREIGN KEY (captain_id) REFERENCES members(id)"
        ]
    }
}