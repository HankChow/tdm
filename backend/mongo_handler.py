#!/usr/bin/env python3

import pymongo

import config


class MongoHandler(object):
    def __init__(self, db=None, collection=None):
        self.host = config.MONGODB_HOST
        self.port = config.MONGODB_PORT
        self.client = pymongo.MongoClient("mongodb://{host}:{port}/".format(
            host=self.host,
            port=self.port
        ))
        self.db = self.client[db if db else config.MONGODB_DB]
        self.collection = self.db[collection if collection else config.MONGODB_COLLECTION]