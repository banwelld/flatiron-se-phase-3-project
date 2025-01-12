TABLE_DEFINITIONS = {
    "members": {
        "id": "INTEGER PRIMARY KEY",
        "first_name": "TEXT NOT NULL",
        "last_name": "TEXT NOT NULL",
        "birth_date": "TEXT",
        "team_id": "INTEGER",
        "FOREIGN KEY (team_id)": "REFERENCES teams(id)",
    },
    "teams": {
        "id": "INTEGER PRIMARY KEY",
        "name": "TEXT NOT NULL UNIQUE",
        "city": "TEXT",
        "founded": "TEXT",
    },
}