import pymongo
import json
from pymongo import MongoClient

f = open(r'd:\Programming\Python\pyMQ\settings_mq.json')
settings = json.load(f)
mongoDB_login = settings["mongoDB_login"]

# Create the client
client = MongoClient(f"mongodb+srv://{mongoDB_login}@clusterbotequip.aj1qm.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

# Connect to our database
db = client['airMQ']


def insert_document(collection, data):
    """ Function to insert a document into a collection and
    return the document's id.
    """
    return collection.insert_one(data).inserted_id


def set_user_dbdata(file, data):
    """ Function to set a data into a document and
        return the document's id.
        """
    collection = db['user']
    return collection.update_one({"chat_id": str(file)}, {"$set": data}, upsert=True)


def get_creds_dbdata(marker, data):
    """ Function to set a data into a document and
        return the document's id.
        """
    collection = db['user creds']
    return collection.find_one(marker)[data]


def get_user_dbdata(chat_id, data):
    """ Function to set a data into a document and
        return the document's id.
        """
    collection = db['user']
    return collection.find_one({"chat_id": str(chat_id)})[data]


def set_creds_data(file, data):
    """ Function to set a data into a document and
        return the document's id.
        """
    creds_collection = db['user creds']
    return creds_collection.update_one({'ip': file}, {"$set": data}, upsert=True)


def get_google_token(chat_id):
    """ Function to set a data into a document and
        return the document's id.
        """
    collection = db['user creds']
    return collection.find_one({"chat_id": str(chat_id)})


def set_test_dbdata(file, data):
    """ Function to set a data into a document and
        return the document's id.
        """
    collection = db['Test_data']
    return collection.update_one({"chat_id": str(file)}, {"$set": data}, upsert=True)


def get_test_dbdata(chat_id, data):
    """ Function to set a data into a document and
        return the document's id.
        """
    collection = db['Test_data']
    return collection.find_one({"chat_id": str(chat_id)})[data]

# print(insert_document(series_collection, new_show))
