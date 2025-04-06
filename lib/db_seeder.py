#!/usr/bin/env python3

from models.participant.cls import Participant
from models.team.cls import Team

Participant.delete_table()
Team.delete_table()
Participant.build_table()
Team.build_table()

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
m21 = Participant.create("Ulysse", "Malenfant", "1958-06-06")
m22 = Participant.create("Vicki", "Brown", "1982-04-30")
m23 = Participant.create("Wayne", "Greenstone", "1961-09-12")
m24 = Participant.create("Xaviera", "Sanchez", "1958-04-28")
m25 = Participant.create("Yves", "Belanger", "1971-10-26")
m26 = Participant.create("Zenia", "Barbarrosa", "1965-09-22")

t1 = Team.create("The Aristocrats")
t2 = Team.create("Catch Me If You Can")
t3 = Team.create("The Dropouts")
t4 = Team.create("Down the Rabbit Hole")
t5 = Team.create("The Hooligans")

m27 = Participant.create("Dave", "Banwell", "1975-05-28")
t6 = Team.create("Dave's Team")
t0 = Team.create(id=0, name="Free Agents")

team_lists = [
    (m1, m6, m11, m16, m21),
    (m2, m7, m12, m17, m22),
    (m3, m8, m13, m18, m23),
    (m4, m9, m14, m19, m24),
    (m5, m10, m15, m20, m25),
]

teams = [t1, t2, t3, t4, t5]

for i in range(5):
    for mem in team_lists[i]:
        mem.team_id = teams[i].id
        mem.update()
