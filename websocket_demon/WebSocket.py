# -*- coding: utf-8 -*-
__author__ = 'meanwhile'

"""
Ждет склиентов по websocket
Рассылает все клиентам то что приходит по адрессу http://127.0.0.1:8080/send_broatcast
Присланные методом POST и параметр data_send
"""

from tornado import websocket, web, ioloop
import daemon
import logging
import sys

clients = []

class SendPointSocketHandler(websocket.WebSocketHandler):
    waiters = set()

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return True

    def open(self):
        logging.debug("client connectig")
        SendPointSocketHandler.waiters.add(self)

    def on_close(self):
        logging.debug('cleint closed')
        SendPointSocketHandler.waiters.remove(self)

    @classmethod
    def send_updates(cls, chat):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)



class SendBroatcastUsePOSTHandler(web.RequestHandler):
    def get(self):
        pass

    @web.asynchronous
    def post(self):
        self.finish()
        logging.debug("start post")
        data = self.get_argument('data_send')
        logging.debug("date="+data)
        SendPointSocketHandler.send_updates(data)



app_websocket = web.Application([
        (r'/ws',  SendPointSocketHandler),
])

app_sendbroatcast = web.Application([
        (r'/send_broatcast', SendBroatcastUsePOSTHandler)
])

class WebScoketServerDemon(daemon.Daemon):
    def run(self):
        app_websocket.listen(8080)
        app_sendbroatcast.listen(8081, address='127.0.0.1')
        print('starting loop')
        ioloop.IOLoop.instance().start()
        print 'start loop was'

if __name__ == '__main__':
    daemon = WebScoketServerDemon('/tmp/daemon-websoket.pid', stdout='/var/log/vk_parser/wsocket_stdout.log',
                            stderr='/var/log/vk_parser/wsocket_error.log')
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