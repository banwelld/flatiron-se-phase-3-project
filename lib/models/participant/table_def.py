table_def = {
    "table_name": "participants",
    "columns": {
        "id": "INTEGER PRIMARY KEY",
        "first_name": "TEXT",
        "last_name": "TEXT",
        "birth_date": "TEXT",
        "team_id": "INTEGER",
    },
    "foreign_keys": [
        "FOREIGN KEY (team_id) REFERENCES teams(id)",
    ],
}
