import argparse

from challengeme.handlers.datahandler import DataHandler
from challengeme.handlers.commandhandler import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_getlang = subparsers.add_parser('get-languages')
    parser_getlang.set_defaults(func=get_languages)

    parser_addlang = subparsers.add_parser('add-language')
    parser_addlang.add_argument('language')
    parser_addlang.set_defaults(func=add_language)

    parser_getchall = subparsers.add_parser('get-challenges')
    parser_getchall.set_defaults(func=get_challenges)

    # TODO: ask for description, notes and language constraints.
    parser_addchall = subparsers.add_parser('add-challenge')
    parser_addchall.set_defaults(func=add_challenge)

    parser_delchall = subparsers.add_parser('delete-challenge')
    parser_delchall.set_defaults(func=del_challenge)

    # TODO: add further options for challenge set, language, or modifier.
    parser_pick = subparsers.add_parser('pick-challenge')
    parser_pick.set_defaults(func=pick_challenge)

    parser_active = subparsers.add_parser('active-challenges')
    parser_active.set_defaults(func=active_challenges)

    parser_complete = subparsers.add_parser('completed-challenges')
    parser_complete.set_defaults(func=completed_challenges)

    # TODO: this will give a menu of which challenge to set as finished.
    parser_finish = subparsers.add_parser('set-finished')
    parser_finish.set_defaults(func=set_finished)

    args = parser.parse_args()
    args.func(args)
