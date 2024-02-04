#!/bin/bash

killall gunicorn
gunicorn --bind 0.0.0.0:8000 config.wsgi -c config/gunicorn.conf.py --daemon && gunicorn --bind 0.0.0.0:8001 config.wsgi_dashboard -c config/gunicorn.conf.py --daemon && gunicorn --bind 0.0.0.0:8002 config.wsgi_cloud -c config/gunicorn.conf.py --daemon && gunicorn --bind 0.0.0.0:8003 config.wsgi_api -c config/gunicorn.conf.py --daemon  && echo "gunicorn started :)"
