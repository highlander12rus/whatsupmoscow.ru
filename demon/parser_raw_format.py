# -*- coding: utf-8 -*-
__author__ = 'meanwhile'

import datetime
import FileWriter
import ProvaderStorage
import math

"""
Парсит сырые даныне и вставляет в бд
Создавать Индлекс на поле date !!!!
"""

files_insert = [
    '01-12-2013.vkr',
    '02-12-2013.vkr',
    '03-12-2013.vkr',
    '04-12-2013.vkr',
    '05-12-2013.vkr',
    '06-12-2013.vkr',
    '07-12-2013.vkr',
    '08-12-2013.vkr',
    '09-12-2013.vkr',
]

def round_float(a):
    return int(a * 100000) / 100000.0

provaderStorage = ProvaderStorage.ProvaderStorage()
provaderStorage.deleteCollections('moscow')

for file in files_insert:
    fileReader = FileWriter.FileWriterBinary("/home/vk_demon/" + file)
    unpack_file = fileReader.read()
    for date_file in unpack_file:
        date_timestamp = datetime.datetime.fromtimestamp(date_file[0])
        lat = round_float(date_file[1] / 10e6)
        lng = round_float(date_file[2] / 10e6)
        provaderStorage.add('moscow', lat, lng, date_timestamp)
print "Complited"