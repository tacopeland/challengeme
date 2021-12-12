import argparse

from challengeme.handlers.datahandler import DataHandler
from challengeme.handlers.commandhandler import CommandHandler

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_foo = subparsers.add_parser('get-languages')
    parser_foo.set_defaults(func=get_languages)

    parser_foo = subparsers.add_parser('add-language')
    parser_foo.add_argument('language')
    parser_foo.set_defaults(func=add_language)

    parser_foo = subparsers.add_parser('get-challenges')
    parser_foo.set_defaults(func=get_challenges)

    # TODO: ask for description, notes and language constraints.
    parser_foo = subparsers.add_parser('add-challenge')
    parser_foo.add_argument('challenge')
    parser_foo.set_defaults(func=add_challenge)

    # TODO: add further options for challenge set, language, or modifier.
    parser_foo = subparsers.add_parser('pick-challenge')
    parser_foo.set_defaults(func=pick_challenge)

    parser_foo = subparsers.add_parser('active-challenges')
    parser_foo.set_defaults(func=active_challenges)

    # TODO: this will give a menu of which challenge to set as finished.
    parser_foo = subparsers.add_parser('set-finished')
    parser_foo.set_defaults(func=set_finished)

    args = parser.parse_args()
    args.func(args)

    '''
    # This will do until I start using setuptools data files
    # https://setuptools.pypa.io/en/latest/userguide/datafiles.html
    datahandler = DataHandler("defaults", "data.db")
    con = datahandler.load_db()
    challenges = datahandler.get_challenges
    challenge_sets = datahandler.get_challenge_sets(con)
    languages = datahandler.get_languages(con)

    datahandler.unload_db(con)
    '''
