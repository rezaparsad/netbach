#!/bin/bash

killall gunicorn
venv/bin/gunicorn --bind 0.0.0.0:8000 config.wsgi -c config/gunicorn.conf.py --daemon && venv/bin/gunicorn --bind 0.0.0.0:8001 config.wsgi_panel -c config/gunicorn.conf.py --daemon && echo "gunicorn started :)"
