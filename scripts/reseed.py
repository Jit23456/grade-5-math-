# -*- coding: utf-8 -*-
"""Clears the curriculum chapters/questions and reseeds them from the current
data/seed.json, without touching the users table (so existing teacher logins
survive). Only ever removes rows tagged source='curriculum' — a chapter or
question a teacher has written or edited is left alone. Run from the
math5-platform directory:

    python scripts/reseed.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app  # noqa: E402


def main():
    con = app.sqlite3.connect(app.DB_PATH)
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(app.SCHEMA)
    for tbl in ("chapters", "questions"):
        try:
            con.execute("ALTER TABLE %s ADD COLUMN visual TEXT NOT NULL DEFAULT ''" % tbl)
        except app.sqlite3.OperationalError:
            pass
    before = con.execute("SELECT COUNT(*) FROM chapters WHERE source='curriculum'").fetchone()[0]
    con.execute("DELETE FROM chapters WHERE source='curriculum'")
    con.commit()
    con.close()
    print("removed %d curriculum chapters (and their questions, by cascade)" % before)
    app.init_db()


if __name__ == "__main__":
    main()
