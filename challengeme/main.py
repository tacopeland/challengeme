from handlers.datahandler import DataHandler

if __name__ == "__main__":
    datahandler = DataHandler("defaults", "data.db")
    con = datahandler.load_db()

    datahandler.unload_db(con)
