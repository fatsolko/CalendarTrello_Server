import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_LOGIN = os.getenv('MONGODB_LOGIN')
MONGO_INITDB_ROOT_USERNAME = os.getenv('MONGO_INITDB_ROOT_USERNAME')
MONGO_INITDB_ROOT_PASSWORD = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
MONGO_INITDB_ROOT_IP = os.getenv('MONGO_INITDB_ROOT_IP')
# Create the client
client = MongoClient(f"mongodb+srv://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}"
                     f"@{MONGO_INITDB_ROOT_IP}/?authMechanism=DEFAULT")
# MONGODB_LOGIN = os.getenv("MONGODB_LOGIN")
# # Create the client
# client = MongoClient(f"mongodb+srv://{MONGODB_LOGIN}@clusterbotequip.aj1qm.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")

# Connect to our database
db = client['CalendarTrello']


def insert_document(collection, data):
    """ Function to insert a document into a collection and
    return the document's id.
    """
    return collection.insert_one(data).inserted_id


def set_user_db_data(file, data):
    """ Function to set a data into a document and
        return the document's id.
        """
    collection = db['user']
    return collection.update_one({"chat_id": str(file)}, {"$set": data}, upsert=True)


def get_creds_db_data(marker, data):
    """ Function to set a data into a document and
        return the document's id.
        """
    collection = db['user creds']
    return collection.find_one(marker)[data]


def get_user_db_data(chat_id, data):
    """ Function to set a data into a document and
        return the document's id.
        """
    collection = db['user']
    return collection.find_one({"chat_id": str(chat_id)})[data]


def set_creds_db_data(file, data):
    """ Function to set a data into a document and
        return the document's id.
        """
    creds_collection = db['user creds']
    return creds_collection.update_one({'chat_id': file}, {"$set": data}, upsert=True)


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
