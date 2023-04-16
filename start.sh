#!/bin/bash
# サーバ作成用
#
#1. プロジェクト作成
django-admin startproject commviz .
#2. サーバ作成
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

#アプリケーションサーバ作成
python manage.py startapp commviz_server
