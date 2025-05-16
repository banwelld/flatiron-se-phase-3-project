#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from models import Participant, Team


def seed_db():
    m1 = Participant.create("Andrew", "Smith", "1992-05-06")
    m2 = Participant.create("Brandie", "Jones", "1991-11-09")
    m3 = Participant.create("Chuck", "Johnson", "1998-07-23")
    m4 = Participant.create("Dorothy", "Walker", "1999-09-06")
    m5 = Participant.create("Evan", "Roberts", "1999-12-03")
    m6 = Participant.create("Fiona", "Williams", "1999-03-03")
    m7 = Participant.create("Greg", "St. Dennis", "1999-02-13")
    m8 = Participant.create("Hermoine", "Kemble", "2000-02-23")
    m9 = Participant.create("Ian", "Carson", "2000-12-05")
    m10 = Participant.create("Janice", "Black", "1999-04-28")
    m11 = Participant.create("Kenny", "White", "1995-05-21")
    m12 = Participant.create("Lourda", "Grey", "1983-06-11")
    m13 = Participant.create("Martin", "Oliver", "1995-01-02")
    m14 = Participant.create("Natalie", "Kimmel", "1998-12-22")
    m15 = Participant.create("Oscar", "O'Brien", "1995-11-22")
    m16 = Participant.create("Patty", "Myers", "1997-03-03")
    m17 = Participant.create("Quentin", "Winter", "1999-02-03")
    m18 = Participant.create("Rita", "Haskell", "1967-01-29")
    m19 = Participant.create("Stuart", "Branch", "1978-11-23")
    m20 = Participant.create("Tina", "Harris-Jones", "1979-07-21")

    t1 = Team.create("The Aristocrats")
    t2 = Team.create("Catch Me If You Can")
    t3 = Team.create("The Dropouts")
    t4 = Team.create("Down the Rabbit Hole")
    t5 = Team.create("The Hooligans")

    team_lists = [
        (m1, m6, m11, m16),
        (m2, m7, m12, m17),
        (m3, m8, m13, m18),
        (m4, m9, m14, m19),
        (m5, m10, m15, m20),
    ]

    teams = [t1, t2, t3, t4, t5]

    for i in range(5):
        for mem in team_lists[i]:
            teams[i].append_participant(mem, do_persist=True)


if __name__ == "__main__":
    seed_db()
