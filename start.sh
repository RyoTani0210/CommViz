#!/bin/bash
#1. プロジェクト作成
django-admin startproject commviz .
#2. サーバ作成
python manage.py migrate
#3. 管理画面にスーパーユーザ作成
python manage.py createsuperuser
#アプリケーションサーバ作成
python manage.py startapp commviz-server
