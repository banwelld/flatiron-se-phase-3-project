import sqlite3
from pathlib import Path

DB_FILEPATH = Path(__file__).parent / "data" / "trivia_league.db"

CONN = sqlite3.connect(DB_FILEPATH)
CURSOR = CONN.cursor()
