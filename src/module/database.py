from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Any, Dict, List, Optional


class PyMongoClient:
    def __init__(self, uri: str, database_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[database_name]

    def get_collection(self, collection_name: str) -> Collection:
        return self.db[collection_name]

    def insert_one(self, collection_name: str, document: Dict[str, Any]) -> None:
        collection = self.get_collection(collection_name)
        collection.insert_one(document)

    def insert_many(self, collection_name: str, documents: List[Dict[str, Any]]) -> None:
        collection = self.get_collection(collection_name)
        collection.insert_many(documents)

    def find_one(self, collection_name: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        collection = self.get_collection(collection_name)
        return collection.find_one(query)

    def find_many(self, collection_name: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        collection = self.get_collection(collection_name)
        return list(collection.find(query))

    def update_one(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> None:
        collection = self.get_collection(collection_name)
        collection.update_one(query, {'$set': update})

    def update_many(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> None:
        collection = self.get_collection(collection_name)
        collection.update_many(query, {'$set': update})

    def delete_one(self, collection_name: str, query: Dict[str, Any]) -> None:
        collection = self.get_collection(collection_name)
        collection.delete_one(query)

    def delete_many(self, collection_name: str, query: Dict[str, Any]) -> None:
        collection = self.get_collection(collection_name)
        collection.delete_many(query)