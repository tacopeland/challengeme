import random

import challengeme.config
from challengeme.exceptions import CorruptDatabaseError, AlreadyInDBError
from challengeme.handlers.datahandler import DataHandler

def get_languages(args):
    datahandler = DataHandler(challengeme.config.defaultsdir,
                             challengeme.config.dbfile)
    con = datahandler.load_db()

    languages = list(map(lambda x : x[1], datahandler.get_languages(con)))
    print("The saved programming languages are:\n" + str(languages))

    datahandler.unload_db(con)

def add_language(args):
    datahandler = DataHandler(challengeme.config.defaultsdir,
                             challengeme.config.dbfile)
    con = datahandler.load_db()

    try:
        print(f"Adding language {args.language} to the database.")
        datahandler.add_language(con, args.language)
    except AlreadyInDBError:
        print(f"Error: {args.language} is already in the database.")

    datahandler.unload_db(con)

def get_challenges(args):
    datahandler = DataHandler(challengeme.config.defaultsdir,
                             challengeme.config.dbfile)
    con = datahandler.load_db()

    challenges = datahandler.get_challenges(con)

    print(f"There are a total of {len(challenges)} challenges:")
    for challenge in challenges:
        print(f"""
Challenge: {challenge.description}
Notes: {challenge.notes}
Language constraints: {challenge.language_constraints}
              """)

    datahandler.unload_db(con)

def add_challenge(args):
    datahandler = DataHandler(challengeme.config.defaultsdir,
                             challengeme.config.dbfile)
    con = datahandler.load_db()

    print("Enter the challenge info:")

    desc = ""
    while len(desc) == 0:
        desc = input("Description: ")

    notes = input("Notes: ")
    langs = input("Language constraints (space-separated): ")
    if len(langs) > 0:
        langs = langs.split(" ")
    else:
        langs = []

    try:
        datahandler.add_challenge(con, 1, desc, notes, langs)
    except AlreadyInDBError:
        print("A challenge with this description has already been added.")
    datahandler.unload_db(con)

def del_challenge(args):
    """
    2. Let the user enter a number to delete.
    """
    datahandler = DataHandler(challengeme.config.defaultsdir,
                             challengeme.config.dbfile)
    con = datahandler.load_db()

    # Get self-made challenges
    challenges = datahandler.get_challenges(con)
    set_id = datahandler.get_challenge_set_id(con, challengeme.config.personal)
    challenges = [chall for chall in challenges if chall.set_id == set_id]

    # Print self-made challenges and number them.
    if len(challenges) == 0:
        print(f"You have no self-made challenges, exiting...")
        return

    for (i, chall) in enumerate(challenges):
        print(f"[{i}] {chall.description})")

    # Let the user pick one to delete.
    input_success = False
    while not input_success:
        to_delete = input("Enter the number of the challenge to delete, "
                          "or q to quit: ")
        if to_delete == "q":
            return
        try:
            to_delete = int(to_delete)
            if to_delete >= len(challenges):
                print("That challenge does not exist.")
                continue
            input_success = True
        except ValueError:
            print("That input is not a number!")

    confirm = input(f"Delete challenge {to_delete}? [y/n] ")
    if confirm.lower() == "y":
        datahandler.del_challenge(con, challenges[to_delete].id)
        print(f"Challenge deleted.")

    datahandler.unload_db(con)

def pick_challenge(args):
    datahandler = DataHandler(challengeme.config.defaultsdir,
                             challengeme.config.dbfile)
    con = datahandler.load_db()

    # Get all unstarted challenges
    challenges = [chall for chall in datahandler.get_challenges(con)
                 if chall.date_started is None]
    challenge = random.choice(challenges)

    languages = [lang[1] for lang in datahandler.get_languages(con)]
    if len(languages) == 0:
        print("You have not added any languages!")
        print(f"python ./{args.prog} add-language <language>")

    if len(challenge.language_constraints) != 0:
        languages = [lang for lang in languages
                     if lang in challenge.language_constraints]

        # If there are no languages meeting the language constraints
        if len(languages) == 0:
            pick_challenge(args)
            return

    language = random.choice(languages)

    print("Your task is:")
    print(f"{challenge.description}")
    print(f"({challenge.notes})")
    print(f"Language: {language}")

    accept = input("Do you choose to accept it? [y/n] ")
    if accept.lower() == "y":
        datahandler.accept_challenge(con, challenge.id, language)
        print("Challenge accepted.")

    datahandler.unload_db(con)

def active_challenges(args):
    datahandler = DataHandler(challengeme.config.defaultsdir,
                             challengeme.config.dbfile)
    con = datahandler.load_db()

    challenges = [chall for chall in datahandler.get_challenges(con)
                 if chall.date_started is not None]

    print("Here are your actively running challenges:")
    for chall in challenges:
        print(f"[{chall.language_used}] {chall.description}")
        print(f"\tStarted: {chall.date_started}")

    datahandler.unload_db(con)

def set_finished(args):
    datahandler = DataHandler(challengeme.config.defaultsdir,
                             challengeme.config.dbfile)
    con = datahandler.load_db()

    # Get active challenges
    challenges = [chall for chall in datahandler.get_challenges(con)
                 if chall.date_started is not None]

    if len(challenges) == 0:
        print(f"You have no active challenges, exiting...")
        return

    # Print challenges and number them.
    for (i, chall) in enumerate(challenges):
        print(f"[{i}] {chall.description})")

    # Let the user pick one to finish.
    input_success = False
    while not input_success:
        to_finish = input("Enter the number of the challenge to finish, "
                          "or q to quit: ")
        if to_finish == "q":
            return
        try:
            to_finish = int(to_finish)
            if to_finish >= len(challenges):
                print("That challenge does not exist.")
                continue
            input_success = True
        except ValueError:
            print("That input is not a number!")

    confirm = input(f"Finish challenge {to_finish}? [y/n] ")
    if confirm.lower() == "y":
        datahandler.finish_challenge(con, challenges[to_finish].id)
        print(f"Challenge marked as finished.")

    datahandler.unload_db(con)

def completed_challenges(args):
    datahandler = DataHandler(challengeme.config.defaultsdir,
                             challengeme.config.dbfile)
    con = datahandler.load_db()

    challenges = [chall for chall in datahandler.get_challenges(con)
                 if chall.date_finished is not None]

    print("Here are your completed challenges:")
    for chall in challenges:
        print(f"[{chall.language_used}] {chall.description}")
        print(f"\tStarted: {chall.date_started}")
        print(f"\tFinished: {chall.date_started}")

    datahandler.unload_db(con)
