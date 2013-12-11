# -*- coding: utf-8 -*-

__author__ = 'meanwhile'

import ssl
import time
import socket
import sys
import logging

import vkontakte
import ProvaderStorage
import Constants
import FileWriter
import ProccessingResponce
import daemon


class VkParserDemon(daemon.Daemon):
    def run(self):
        #read code for method vk.executin from file

        codeFromFile = ''
        with open(Constants.Constants.getFileCodeExecute(), 'r') as f:
            codeFromFile = f.read()

        #read access token from file
        access_tokens = [];
        with open(Constants.Constants.getFileAccessToken(), 'r') as f:
            access_tokens = [token.strip() for token in f]

        isValidToken = False;
        for acces_token in access_tokens:
            try:
                vk = vkontakte.API(token=acces_token)
                vk.getServerTime() #проверяем соединилось ли
                isValidToken = True
                break
            except vkontakte.VKError, e:
                logging.error("vkontakte.VKError ")
            except ssl.SSLError, e: #The handshake operation timed out
                logging.error("ssl error")
                time.sleep(1)
                access_tokens.append(acces_token)

        if (isValidToken):
            storage = ProvaderStorage.ProvaderStorage()
            lastTime = vk.getServerTime()
            emptyLastTime = 0;
            while True:
                try:
                    time.sleep(Constants.Constants.getTimeOutInSec())
                    codeSending = codeFromFile.replace('%time_replace%', str(lastTime))
                    json = vk.execute(code=codeSending, timeout=10)
                    logging.debug("vk_json responce ", json)
                    fileName = Constants.Constants.getDirHomeScript() + str(time.strftime("%d-%m-%Y")) + ".vkr" #vk raw
                    file = FileWriter.FileWriterBinary(fileName)
                    process = ProccessingResponce.ProccessingResponce(storage, file)
                    process.jsonParse(json)

                    if json['max_time'] > 0:
                        lastTime = json['max_time'] + 1
                    else:
                        logging.debug("empty json= ", json)

                    logging.debug("lastTime= ", lastTime)
                    logging.debug("complidet proccessing")
                except ssl.SSLError, e:
                    logging.error("ssl error")
                except socket.timeout, e:
                    logging.error("socket.timeout")
                except vkontakte.VKError, e:
                    logging.error("vkontakte.VKError")
                except AttributeError, e:
                    logging.error("AttributeError")
        else:
            #TODO: send emails tokens no correct
            logging.error("token uncorrect")


if __name__ == "__main__":
    logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.ERROR)

    daemon = VkParserDemon('/tmp/daemon-example.pid', stdout='/var/log/vk_parser/stdout.log',
                           stderr='/var/log/vk_parser/error.log')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
