#!/bin/sh
sleep 10

echo "Executing database migrations..."

# Запускаем миграции Alembic
alembic upgrade head
# Проверяем успешность выполнения миграций
if [ $? -ne 0 ]; then
    echo "Migrations failed. Exiting."
    exit 1
fi

echo "Migrations succeeded. Starting the application..."

# Запускаем приложение
python3 ./app/bot.py
