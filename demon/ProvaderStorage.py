# -*- coding: utf-8 -*-
__author__ = 'Meanwhile'

import pymongo
import Constants


#create dabases use vk_parser
#loc : [ <longitude> , <latitude> ]
'''
СОздать индекс на дату
'''

class ProvaderStorage:

    def __init__(self):
        self.client = pymongo.MongoClient(Constants.Constants.getMongoServer(),
                                          Constants.Constants.getMongoPort())
        self.db = self.client['vk_parser'];


    def searchByDate(self, collection, date):
        return self.db[collection].find({"date": date})

    def add(self, collection, lat, lng, date):
        self.db[collection].insert({
        "loc": [lng, lat],
        "date":date
        })

    def findAll(self, collection):
        return self.db[collection].find()

    def deleteCollections(self, collection):
        """ Удаляет выбранную коллекцию
        :param collection имя коллекции
        :type string
        """
        self.db[collection].remove()

