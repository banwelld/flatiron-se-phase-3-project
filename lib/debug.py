#!/usr/bin/env python3

from models.member import Member
from models.team import Team
import ipdb

team1 = Team("The Aristocrats", "mem11")
team2 = Team("Catch Me If You Can", "mem05")
team3 = Team("The Dropouts", "mem15")
team4 = Team("Down the Rabbit Hole", "mem02")

mem01 = Member("Andrew", "Smith", "1992/05/06", team4)
mem02 = Member("Brandie", "Jones", "1991/11/09", team4)
mem03 = Member("Chuck", "Johnson", "1998/07/23", team1)
mem04 = Member("Dorothy", "Walker", "1999/09/06", team3)
mem05 = Member("Evan", "Roberts", "1999/12/03", team2)
mem06 = Member("Fiona", "Williams", "1999/03/03", team3)
mem07 = Member("Greg", "St. Dennis", "1999/02/13", team4)
mem08 = Member("Hermoine", "Kemble", "2000/02/23", team1)
mem09 = Member("Ian", "Carson", "2000/12/05", team2)
mem10 = Member("Janice", "Black", "1999/04/28", team1)
mem11 = Member("Kenny", "White", "1995/05/21", team1)
mem12 = Member("Lourda", "Grey", "1983/06/11", team3)
mem13 = Member("Martin-Pierre", "Oliver", "1995/01/02", team2)
mem14 = Member("Natalie", "Kimmel", "1998/12/22", team4)
mem15 = Member("Oscar", "O'Brien", "1995/11/22", team3)
mem16 = Member("Patty", "Myers", "1997/03/03", team2)


ipdb.set_trace()