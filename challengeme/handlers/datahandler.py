from ..exceptions import CorruptDatabaseError, AlreadyInDBError
from ..challenges import Challenge

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
                           description text NOT NULL UNIQUE,
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

    def get_languages(self, con):
        cur = con.cursor()
        cur.execute("SELECT * FROM languages;")

        return list(cur.fetchall())

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

    def get_challenges(self, con):
        cur = con.cursor()
        cur.execute("SELECT * FROM challenges;")

        res = []
        for row in cur.fetchall():
            langs = [] if len(row[4]) == 0 else row[4].split(',')
            res.append(Challenge(row[0], row[1], row[2], row[3],
                              langs, row[5], row[6], row[7]))
        return res

    def add_challenge(self, con, set_id, desc, notes="", langs=[]):
        cur = con.cursor()
        if self.get_challenge_id(con, desc) is not None:
            raise AlreadyInDBError(f"Challenge {desc} is already in the DB")

        cur.execute("""INSERT INTO challenges(set_id,
                                              description,
                                              notes,
                                              language_constraints)
                       VALUES(?,?,?,?);""", (set_id, desc, notes,
                                             ",".join(langs)))
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

    def get_challenge_sets(self, con):
        cur = con.cursor()
        cur.execute("SELECT * FROM challenge_sets;")

        return list(cur.fetchall())

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

        self.__add_challenge_set(con, "Self-added challenges")

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
                    return

                if ("challenges" in chall_data.keys()
                    and len(chall_data["challenges"]) > 0):
                    for chall in chall_data["challenges"]:
                        if "languageConstraints" in chall:
                            langs = chall["languageConstraints"]
                        else:
                            langs = []

                        try:
                            self.add_challenge(con, set_id,
                                               chall["description"],
                                               chall["notes"], langs)
                        except AlreadyInDBError:
                            print("You have a duplicate challenge: "
                                  f"{chall['description']}. "
                                  "It will not be added to the database.",
                                  file=sys.stderr)
                elif "num-challenges" in chall_data.keys():
                    for i in range(chall_data["num-challenges"]):
                        try:
                            name = f'{chall_data["name"]} challenge {i}'
                            self.add_challenge(con, set_id, name, "", [])
                        except AlreadyInDBError:
                            print("Duplicate challenge was added in "
                                  "_load_defaults. This is a bug.")
        cur.close()

    def is_db_valid(self, con):
        cur = con.cursor()
        cur.execute("""SELECT name FROM sqlite_master
                       WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                       ORDER BY 1;""")
        if set(cur.fetchall()) != {('challenge_sets',),
                                   ('challenges',),
                                   ('languages',)}:
            return False

        cur.execute('SELECT * FROM challenge_sets LIMIT 0;')
        challset_cols = [desc[0] for desc in cur.description]
        cur.execute('SELECT * FROM challenges LIMIT 0;')
        chall_cols = [desc[0] for desc in cur.description]
        cur.execute('SELECT * FROM languages LIMIT 0;')
        language_cols = [desc[0] for desc in cur.description]

        if challset_cols != ['id', 'name']:
            return False
        if chall_cols != ['id', 'set_id', 'description', 'notes',
                          'language_constraints', 'date_started',
                          'date_finished', 'language_used']:
            return False
        if language_cols != ['id', 'name']:
            return False

        return True

    def load_db(self):
        load_defaults = False
        if not (os.path.exists(self.dbfile)
                and os.path.isfile(self.dbfile)
                and os.stat(self.dbfile).st_size > 0):
            load_defaults = True

        con = self.__connect_to_db()

        try:
            valid = self.is_db_valid(con)
        except sqlite3.DatabaseError:
            raise CorruptDatabaseError("db_file " + self.dbfile + " corrupted")

        if not load_defaults and not valid:
            raise CorruptDatabaseError("db_file " + self.dbfile + " corrupted")
        elif load_defaults:
            self.__create_tables(con)
            self.__load_defaults(con)
        return con

    def unload_db(self, con):
        con.commit()
        self.__disconnect_from_db(con)
