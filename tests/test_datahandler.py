import os
import tempfile
import sqlite3
import unittest

import context
import challengeme.config
from challengeme.handlers.datahandler import DataHandler
from challengeme.exceptions import CorruptDatabaseError

class TestDataHandler(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.test_dir.cleanup()

    def test_load_unload_db(self):
        db_file = os.path.join(self.test_dir.name, "test_db.db")
        self.assertFalse(os.path.exists(db_file))


        handler = DataHandler('../challengeme/defaults/', db_file)
        con = handler.load_db()

        # Is db file written to?
        self.assertTrue(os.path.exists(db_file))
        self.assertTrue(os.stat(db_file).st_size > 0)

        # Are tables created correctly?
        cur = con.cursor()
        cur.execute("""SELECT name FROM sqlite_master
                       WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                       ORDER BY 1""")
        rows = cur.fetchall()
        self.assertEqual(set(rows),
                         {('challenge_sets',),
                          ('challenges',),
                          ('languages',)})

        cur.execute('SELECT * FROM challenge_sets LIMIT 0;')
        challset_cols = [desc[0] for desc in cur.description]
        cur.execute('SELECT * FROM challenges LIMIT 0;')
        chall_cols = [desc[0] for desc in cur.description]
        cur.execute('SELECT * FROM languages LIMIT 0;')
        language_cols = [desc[0] for desc in cur.description]

        self.assertEqual(challset_cols, ['id', 'name'])
        self.assertEqual(chall_cols,
                         ['id', 'set_id', 'description', 'notes',
                          'language_constraints', 'date_started',
                          'date_finished', 'language_used'])
        self.assertEqual(language_cols, ['id', 'name'])

        handler.unload_db(con)

        # Is connection closed properly?
        with self.assertRaises(sqlite3.ProgrammingError):
            con.cursor()

        os.remove(db_file)

    def test_corrupt_db(self):
        db_file = os.path.join(self.test_dir.name, "test_db.db")
        handler = DataHandler('../challengeme/defaults', db_file)

        with open(db_file, 'w') as fp:
            GARBAGE = "\x42\x11\x95\x23\xff\x08\xdd"
            fp.write(GARBAGE)

        with self.assertRaises(CorruptDatabaseError):
            handler.load_db()

        with open(db_file, 'w') as fp:
            fp.truncate()

        # See if an exception is raised after truncating
        handler.load_db()

    def test_add_challenge(self):
        db_file = os.path.join(self.test_dir.name, "test_db.db")
        handler = DataHandler('../challengeme/defaults/', db_file)
        con = handler.load_db()
        cur = con.cursor()

        CHALL_DESC = "@@@@!@ THIS IS A DUMMY DESCRIPTION @!@@#@"
        CHALL_NOTES = "&&&**# THIS IS A DUMMY NOTE ##(()^"
        CHALL_SET_ID = handler.get_challenge_set_id(config.personal)
        self.assertIsNotNone(CHALL_SET_ID)
        CHALL_LANGS = ["C++", "golang", "brainfuck"]

        self.assertIsNone(handler.get_challenge_id(con, CHALL_DESC))
        handler.add_challenge(con, CHALL_SET_ID, CHALL_DESC, CHALL_NOTES,
                              CHALL_LANGS)
        self.assertIsNotNone(handler.get_challenge_id(con, CHALL_DESC))

        handler.unload_db(con)

if __name__ == "__main__":
    unittest.main()
