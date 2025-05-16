#!/usr/bin/env python3

from models import Participant, Team


def initialize_db():
    Participant.delete_table()
    Team.delete_table()
    Participant.build_table()
    Team.build_table()

    Team.create("FREE AGENT", True)


if __name__ == "__main__":
    initialize_db()
