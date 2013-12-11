# -*- coding: utf-8 -*-
__author__ = 'meanwhile'

import Constants

import math
import datetime
import urllib
import urllib2
import json
import logging


class ProccessingResponce:
    def __init__(self, provaderStorage, fileWriting):
        """
        :param provaderStorage класс доступа к бд
        :type ProvaderStorage.ProvaderStorage()
        :param fileWriting используются для записи в файл
        :type FileWriter.FileWriterBinary()
        """
        self.provaderStorage = provaderStorage
        self.fileWriting = fileWriting

    def jsonParse(self, json):
        """Распарсвиание ответа от вк и сохранения в БД
        :param json Responce from vk
        :type json
        """

        self.placesProccess('moscow', json['moscow']['checkins'])
        self.wallsProccess('moscow', json['moscow']['wals'])

    def placesProccess(self, collection, checkinsArray):
        """Распрасивание овтета котоырй от places
        :param checkinsArray Массив мест из json бьекта
        :type checkinsArray object
        """
        date_for_broatcast = []
        for checkin in checkinsArray:
            date_for_broatcast.append([ checkin['lng'],  checkin['lat']])
            self.__saveInRaw(checkin['lat'], checkin['lng'], checkin['time'])
            self.__saveInDb(collection, checkin['lat'], checkin['lng'], checkin['time'])
        self.__sendBroatcast(date_for_broatcast)


    def __sendBroatcast(self, data):
        """ Рассылка broatcast'a используя демона с websocket'ом
            :param data массив кординат т.е [[lng, lat], [lng, lat]]
            :type array
        """
        if len(data) > 0:
            try:
                data_send = json.dumps(data)
                data_send = urllib.urlencode({"data_send": data_send})
                logging.debug("sendBroatcast", data_send)
                req = urllib2.Request(url=Constants.Constants.getAdressSendBroatcast(), data=data_send)
                urllib2.urlopen(req).read()
            except Exception, e:
                logging.error("sendBroatcast error", e)



    def wallsProccess(self, collection, walsArray):
        """ parase responce wals
        :param walsArray
        :type json
        """
        date_for_broatcast = []
        for wall in walsArray:
            loc = wall['coordinates'].split()
            lat = float(loc[0])
            lng = float(loc[1])
            date_for_broatcast.append([ lng,  lat])
            self.__saveInRaw(lat, lng, wall['time'])
            self.__saveInDb(collection, lat, lng, wall['time'])
        self.__sendBroatcast(date_for_broatcast)

    def round_float(self, a):
        return int(a * 100000) / 100000.0

    def __saveInDb(self, collection, lat, lng, time):
        """
        :param collection имя коллекции в которую вставлять
        :type string
        :param lat кординаты
        :type double
        :param lng кординаты
        :type double
        :param time время в unix timestamp
        :type int
        """
        date_timestamp = datetime.datetime.fromtimestamp(time)
        self.provaderStorage.add(collection, self.round_float(lat), self.round_float(lng), date_timestamp)

    def __saveInRaw(self, lat, lng, time):
        """ Сохраняет даныне в файл
        :param time
        :type int
        :param lat
        :type float
        :param lng
        :type float
        """
        lat = float(lat)
        lng = float(lng)
        lat = lat * 10e6
        lng = lng * 10e6
        self.fileWriting.write(time, lat, lng)

