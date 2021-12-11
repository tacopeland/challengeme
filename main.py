from challengeme.handlers.datahandler import DataHandler

if __name__ == "__main__":
    # This will do until I start using setuptools data files
    # https://setuptools.pypa.io/en/latest/userguide/datafiles.html
    datahandler = DataHandler("defaults", "data.db")
    con = datahandler.load_db()
    datahandler.unload_db(con)
