import sqlite3

CONN = sqlite3.connect('trivia_league.db')
CURSOR = CONN.cursor()