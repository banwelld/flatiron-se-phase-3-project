#!/usr/bin/env python3

from models.member import Member
from models.team import Team
from helpers import *
import ipdb
import os

os.system("clear")

Member.delete_table()
Team.delete_table()
Member.build_table()
Team.build_table()

m1 = Member.create("Andrew", "Smith", "1992/05/06")
m2 = Member.create("Brandie", "Jones", "1991/11/09")
m3 = Member.create("Chuck", "Johnson", "1998/07/23")
m4 = Member.create("Dorothy", "Walker", "1999/09/06")
m5 = Member.create("Evan", "Roberts", "1999/12/03")
m6 = Member.create("Fiona", "Williams", "1999/03/03")
m7 = Member.create("Greg", "St. Dennis", "1999/02/13")
m8 = Member.create("Hermoine", "Kemble", "2000/02/23")
m9 = Member.create("Ian", "Carson", "2000/12/05")
m10 = Member.create("Janice", "Black", "1999/04/28")
m11 = Member.create("Kenny", "White", "1995/05/21")
m12 = Member.create("Lourda", "Grey", "1983/06/11")
m13 = Member.create("Martin", "Oliver", "1995/01/02")
m14 = Member.create("Natalie", "Kimmel", "1998/12/22")
m15 = Member.create("Oscar", "O'Brien", "1995/11/22")
m16 = Member.create("Patty", "Myers", "1997/03/03")
m17 = Member.create("Quentin", "Winter", "1999/02/03")
m18 = Member.create("Rita", "Haskell", "1967/01/29")
m19 = Member.create("Stuart", "Branch", "1978/11/23")
m20 = Member.create("Tina", "Harris-Jones", "1979/07/21")
m21 = Member.create("Ulysse", "Malenfant", "1958/06/06")
m22 = Member.create("Vicki", "Brown", "1982/04/30")
m23 = Member.create("Wayne", "Greenstone", "1961/09/12")
m24 = Member.create("Xaviera", "Sanchez", "1958/04/28")
m25 = Member.create("Yves", "Belanger", "1971/10/26")
m26 = Member.create("Zenia", "Barbarrosa", "1965/09/22")

t1 = Team.create("The Aristocrats")
t2 = Team.create("Catch Me If You Can")
t3 = Team.create("The Dropouts")
t4 = Team.create("Down the Rabbit Hole")
t5 = Team.create("The Hooligans")

m27 = Member.create("Dave", "Banwell", "1975/05/28")
t6 = Team.create("Dave's Team")

ipdb.set_trace()