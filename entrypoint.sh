#!/bin/bash
set -e

echo ">>> 正在收集静态文件..."
python manage.py collectstatic --noinput

echo ">>> 正在执行数据库迁移..."
python manage.py migrate --noinput

echo ">>> 启动 Gunicorn 服务器..."
exec "$@"
