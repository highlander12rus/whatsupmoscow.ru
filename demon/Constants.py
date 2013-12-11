# -*- coding: utf-8 -*-

__author__ = 'ilya'


class Constants:

    @staticmethod
    def getMongoServer():
        return '127.0.0.1'

    @staticmethod
    def getMongoPort():
        return 27017

    @staticmethod
    def getTimeOutInSec():
        return 5

    @staticmethod
    def getDistanceForClustered():
        return 10

    @staticmethod
    def getFileAccessToken():
        return '/home/vk_demon/access_token.txt'

    @staticmethod
    def getFileCodeExecute():
        return '/home/vk_demon/code.txt'

    @staticmethod
    def getDirHomeScript():
        return '/home/vk_demon/'

    @staticmethod
    def getAdressSendBroatcast():
        return 'http://127.0.0.1:8081/send_broatcast'
