# Backspace hackerspace Access Control System

Скрипт загрузки deploy.sh:
`HOST=<raspberry pi hostname> ./deploy.sh`

Скрипт start.sh запускает [modbus2mqtt](https://github.com/mbs38/spicierModbus2mqtt) с конфигурацией, описанной в backspace.csv
При бутстрапе переименовать start.sh.example в start.sh, вписать пути, креды MQTT и параметры порта.

В index.js пример работы с MQTT (при открытии внутренней двери включает свет в тамбуре).

При бутстрапе выполнить npm install.

В usb2all.py расположен старый скрипт, управляющий светом. В migalo2000.service — systemd сервис, запускающий этот скрипт.

