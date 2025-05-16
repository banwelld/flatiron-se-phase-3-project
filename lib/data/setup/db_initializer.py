#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from models import Participant, Team


def initialize_db():
    Participant.del_table()
    Team.del_table()
    Participant.build_table()
    Team.build_table()

    Team.create("FREE AGENT", True)


if __name__ == "__main__":
    initialize_db()
