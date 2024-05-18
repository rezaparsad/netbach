#!/bin/bash


killall screen
killall gunicorn
venv/bin/gunicorn --bind 0.0.0.0:8000 config.wsgi -c config/gunicorn.conf.py --daemon && venv/bin/gunicorn --bind 0.0.0.0:8001 config.wsgi_panel -c config/gunicorn.conf.py --daemon && echo "gunicorn started :)"


sleep 4

screen -dm -S cost_server_cloud python cloud/check_cost_server.py
screen -dm -S notif_charge python panel/notif_charge.py
screen -dm -S bot python bot/bot.py