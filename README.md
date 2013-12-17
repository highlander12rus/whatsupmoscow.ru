whatsupmoscow.ru
================
Демон сбора анимация из Вконтакте и Демон для подержания WebSocket(использует tornado).

Системные требования
-------------------
Python 2, MongoDB 2.4.6 или выше.

Установка
------------
Требуется установка tornado (для WebSocket), vkontakte<br>
`pip install tornado`<br>
`pip install vkontakte`<br>
`pip install pymongo`<br>
Создать папку для логов:<br>
`mkdir /var/log/vk_parser/` (по умолчанию, можно изменить в demon/main.py и в websocket_demon/WebSocket.py)<br>

В MongoDb<br>
Создать  базу данных:<br>
`use vk_parseer`<br>
Создать коллекцию:<br>
`db.moscow.find()` //не совсем содание. создано будет при первой вставки<br>
создать идекс для поля даты, если буедт идти выборка по дате(как у нас)<br>

Запуск
-----
Для запуска демона дял сбора ифны из вк:<br>
`python demon/main.py start`<br>
Запуск WebSocket:<br>
`python websocket_demon/WebSocket.py start`<br>

По умолчанию лог лежит в папке /var/log/vk_parser/


