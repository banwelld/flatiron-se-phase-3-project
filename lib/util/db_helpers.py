from __init__ import CURSOR, CONN


def find_entity_in_list(entities: list, entity_id: int):
    return next((e for e in entities if e.id == entity_id), None)


def create_table(table_def: dict):
    """
    Assembles and executes an SQL query that creates a table from data
    in the provided table definition and commits it to the connected
    database.
    """
    columns = [
        f"{name} {data_type}" for name, data_type in table_def["columns"].items()
    ]

    foreign_keys = table_def.get("foreign_keys", [])
    col_schema = ", ".join(columns + foreign_keys)

    query = f"CREATE TABLE IF NOT EXISTS {table_def['table_name']} ({col_schema})"
    CURSOR.execute(query)
    CONN.commit()


def drop_table(table_def: dict):
    """
    Assembles and executes an SQL query that drops the table specified
    in the provided table definition and commits the change to the
    connected database.
    """
    query = f"DROP TABLE IF EXISTS {table_def['table_name']}"
    CURSOR.execute(query)
    CONN.commit()


def select_all_rows(table_def: dict, team_id: int = None):
    """
    Assembles and executes an SQL query that fetches all rows from the
    table specified in the provided table definition that match the
    provided criteria, if any, returning a list of all matching rows or
    an empty list if no rows matched.
    """
    if team_id is not None:
        where_clause = "WHERE team_id = ?"
        criteria = (team_id,)
    else:
        where_clause = ""
        criteria = ""

    sort_columns = (
        "name" if table_def["table_name"] == "teams" else "last_name, first_name"
    )
    sort_clause = f"ORDER BY {sort_columns}"
    query = f"SELECT * FROM {table_def['table_name']} " f"{where_clause} {sort_clause}"

    return CURSOR.execute(query, criteria).fetchall()


def delete_row(table_def: dict, id: int):
    """
    Assembles and executes an SQL query that deletes the table specified
    in the provided table definition and commits the change to the
    connected database.
    """
    query = f"DELETE FROM {table_def['table_name']} WHERE id = ?"
    CURSOR.execute(query, (id,))
    CONN.commit()


def insert_row(table_def: dict, **criteria):
    """
    Assembles and executes an SQL query that inserts data, from the
    provided key/value criteria, into the table specified in the
    provided table definition and commits the change to the conected
    database.
    """
    columns = ", ".join(criteria.keys())
    wildcards = ", ".join(["?"] * len(criteria.keys()))

    query = f"INSERT INTO {table_def['table_name']} ({columns}) VALUES ({wildcards})"
    CURSOR.execute(query, tuple(criteria.values()))
    CONN.commit()

    return CURSOR.lastrowid


def update_row(table_def: dict, id: int, **updates):
    """
    Assembles and executes an SQL query that updates the data for a row
    in the table specified in the provided table definition and commits
    the change to the connected database. The query filters the table
    for a row matching the provided ID number and updates the fields in
    the columns matching the keys in the keyword criteria.
    """
    assignment_string = ", ".join([f"{col} = ?" for col in updates.keys()])
    where_clause = "WHERE id IS NULL" if id is None else "WHERE id = ?"
    assignment_values = [val for val in updates.values()]

    if id is not None:
        assignment_values.append(id)

    query = (
        f"UPDATE {table_def['table_name']} " f"SET {assignment_string} {where_clause}"
    )

    CURSOR.execute(query, tuple(assignment_values))
    CONN.commit()


def parse_db_row(model: type, record: list):
    """
    Using a record from either the participants or teams table,
    checks if an instance exists in the appropriate repository. If so,
    overwrites the existing instance's attributes and returns early.
    If no matching instance in repository, matches the the database
    record, then instantiates new instance from the record's data and
    adds it to the repository.

    Returns the item instance.
    """
    repository = get_repository(model, record)

    if item := find_entity_in_list(repository, record[0]):
        update_existing_instance(item, model, record)
        return item

    item = create_instance(model, record)
    repository.append(item)
    return item


# utility functions for parse_db_row


def get_repository(model, record):
    from models.participant import Participant
    from models.team import Team

    if model is Participant:
        team = find_entity_in_list(Team.all, record[-1])
        return team.participants
    return Team.all


def update_existing_instance(item, model, record):
    config_keys = list(model.CONFIG.keys())

    for name, attr in model.CONFIG.items():
        is_required = attr.get("req_for_init")
        is_editable = attr.get("user_editable")

        if not is_required and is_editable:
            continue

        attr_index = config_keys.index(name)

        if attr_index >= len(record) - 1:
            continue

        value = record[attr_index]
        setattr(item, name, value)


def create_instance(model, record):
    field_list = (
        tuple(record[1:]) if model.__name__.lower() == "team" else tuple(record[1:-1])
    )
    item = model(*field_list)
    item.id = record[0]
    return item
