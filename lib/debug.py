#!/usr/bin/env python3

from models.member import Member
from models.team import Team
import ipdb

Member.delete_table()
Team.delete_table()
Member.build_table()
Team.build_table()

Member.create("Andrew", "Smith", "1992/05/06")
Member.create("Brandie", "Jones", "1991/11/09")
Member.create("Chuck", "Johnson", "1998/07/23")
Member.create("Dorothy", "Walker", "1999/09/06")
Member.create("Evan", "Roberts", "1999/12/03")
Member.create("Fiona", "Williams", "1999/03/03")
Member.create("Greg", "St. Dennis", "1999/02/13")
Member.create("Hermoine", "Kemble", "2000/02/23")
Member.create("Ian", "Carson", "2000/12/05")
Member.create("Janice", "Black", "1999/04/28")
Member.create("Kenny", "White", "1995/05/21")
Member.create("Lourda", "Grey", "1983/06/11")
Member.create("Martin-Pierre", "Oliver", "1995/01/02")
Member.create("Natalie", "Kimmel", "1998/12/22")
Member.create("Oscar", "O'Brien", "1995/11/22")
Member.create("Patty", "Myers", "1997/03/03")

Team.create("The Aristocrats")
Team.create("Catch Me If You Can")
Team.create("The Dropouts")
t4 = Team.create("Down the Rabbit Hole")

mem17 = Member.create("Dave", "Banwell", "1975/05/28")
mem17.join_team(t4)

ipdb.set_trace()