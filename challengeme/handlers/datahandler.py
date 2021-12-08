import json
from pathlib import Path
import os
import sqlite3
import sys

class DataHandler:
    """Handle reading and writing saved challenge data."""

    def __init__(self, defaultsdir, dbfile):
        self.defaultsdir = defaultsdir
        self.dbfile = dbfile
        self.challenges = []

    def __connect_to_db(self):
        try:
            con = sqlite3.connect(self.dbfile)
        except sqlite3.Error as err:
            print(err, file=sys.stderr)
        return con

    def __disconnect_from_db(self, con):
        if con:
            con.close()

    def __create_tables(self, con):
        cursor = con.cursor()
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS challenge_sets (
                           id integer PRIMARY KEY,
                           name text NOT NULL
                      );
                       """)
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS languages (
                           id integer PRIMARY KEY,
                           name text NOT NULL
                      );
                       """)
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS challenges (
                           id integer PRIMARY KEY,
                           set_id integer NOT NULL,
                           description text NOT NULL,
                           notes text,
                           language_constraints text,
                           date_started text,
                           date_finished text,
                           language_used integer,
                           FOREIGN KEY (set_id) REFERENCES challenge_sets (id)
                      );
                       """)

    def __load_defaults(self, con):
        cur = con.cursor()

        default_files = Path(self.defaultsdir).glob("*.json")
        for file in default_files:
            with open(file, encoding="utf8") as data_fp:
                chall_data = json.load(data_fp)

                cur.execute("INSERT INTO challenge_sets(name) VALUES(?);",
                           (chall_data["name"], ))
                cur.execute("SELECT id FROM challenge_sets WHERE name = ?;",
                           (chall_data["name"], ))
                set_id = cur.fetchone()[0]

                for chall in chall_data["challenges"]:
                    if "languageConstraints" in chall:
                        langs = ",".join(chall["languageConstraints"])
                    else:
                        langs = ""

                    cur.execute(
                        """INSERT INTO challenges(set_id,
                                                  description,
                                                  notes,
                                                  language_constraints)
                           VALUES (?,?,?,?);""",
                        (set_id, chall["description"], chall["notes"], langs))

    def load_db(self):
        load_defaults = False
        if not (os.path.exists(self.dbfile) and os.path.isfile(self.dbfile)):
            load_defaults = True

        con = self.__connect_to_db()
        if load_defaults:
            print("Creating and initializing database...")
            self.__create_tables(con)
            self.__load_defaults(con)
        return con

    def unload_db(self, con):
        con.commit()
        self.__disconnect_from_db(con)
