import json
from pathlib import Path
import os
import sqlite3
import sys

class AlreadyInDBError(Exception):
    pass

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
        cur = con.cursor()
        cur.execute("""
                       CREATE TABLE IF NOT EXISTS challenge_sets (
                           id integer PRIMARY KEY,
                           name text NOT NULL
                      );
                       """)
        cur.execute("""
                       CREATE TABLE IF NOT EXISTS languages (
                           id integer PRIMARY KEY,
                           name text NOT NULL
                      );
                       """)
        cur.execute("""
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
        cur.close()

    def get_language_id(self, con, name):
        cur = con.cursor()
        cur.execute("SELECT id FROM languages WHERE name = ?;", (name,))

        row = cur.fetchone()
        if row is None:
            lang_id = None
        else:
            lang_id = row[0]

        cur.close()
        return lang_id

    def add_language(self, con, name):
        cur = con.cursor()
        if self.get_language_id(con, name) is not None:
            raise AlreadyInDBError(f"Language {name} is already in the DB")

        cur.execute("INSERT INTO languages(name) VALUES(?);", (name,))
        cur.close()
        return self.get_language_id(con, name)

    def get_challenge_id(self, con, desc):
        cur = con.cursor()
        cur.execute("SELECT id FROM challenges WHERE description = ?;",
                    (desc,))

        row = cur.fetchone()
        if row is None:
            challenge_id = None
        else:
            challenge_id = row[0]

        cur.close()
        return challenge_id

    def add_challenge(self, con, set_id, desc, notes="", langs=""):
        cur = con.cursor()
        if self.get_challenge_id(con, desc) is not None:
            raise AlreadyInDBError(f"Challenge {desc} is already in the DB")

        cur.execute("""INSERT INTO challenges(set_id,
                                              description,
                                              notes,
                                              language_constraints)
                       VALUES(?,?,?,?);""", (set_id, desc, notes, langs))
        cur.close()
        return self.get_challenge_id(con, desc)

    def get_challenge_set_id(self, con, name):
        cur = con.cursor()
        cur.execute("SELECT id FROM challenge_sets WHERE name = ?;", (name,))

        row = cur.fetchone()
        if row is None:
            set_id = None
        else:
            set_id = row[0]

        cur.close()
        return set_id

    def __add_challenge_set(self, con, name):
        cur = con.cursor()
        if self.get_challenge_set_id(con, name) is not None:
            raise AlreadyInDBError(f"Challenge set {name} is already in the DB")

        cur.execute("INSERT INTO challenge_sets(name) VALUES(?);", (name,))
        cur.execute("SELECT id FROM challenge_sets WHERE name = ?", (name,))
        set_id = cur.fetchone()[0]
        cur.close()
        return set_id

    def __load_defaults(self, con):
        cur = con.cursor()

        default_files = Path(self.defaultsdir).glob("*.json")
        for file in default_files:
            with open(file, encoding="utf8") as data_fp:
                chall_data = json.load(data_fp)

                try:
                    set_id = self.__add_challenge_set(con, chall_data["name"])
                except AlreadyInDBError:
                    print(f"You have a duplicate challenge set in file {file}."
                          " It will not be added to the database.",
                         file=sys.stderr)
                else: 
                    for chall in chall_data["challenges"]:
                        if "languageConstraints" in chall:
                            langs = ",".join(chall["languageConstraints"])
                        else:
                            langs = ""

                        try:
                            self.add_challenge(con, set_id, chall["description"],
                                               chall["notes"], langs)
                        except AlreadyInDBError:
                            print("You have a duplicate challenge: "
                                  f"{chall['description']}. "
                                  "It will not be added to the database.",
                                  file=sys.stderr)
        cur.close()

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
