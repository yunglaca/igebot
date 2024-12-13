#!make

.PHONY: .env
.env:
	@if [ ! -f ./.env ]; then \
		echo "Please create and fill .env file!" && exit 1; \
	fi

include .env

.PHONY: venv
venv:
	rm -rf venv
	python3.12 -m venv ./venv
	. venv/bin/activate; pip install -r requirements.txt

start_bot:
	PYTHONPATH="${PYTHONPATH}:/home/laca/test-async-alembic/app/" python3.12 ./app/bot.py

start_bot2:
	PYTHONPATH="${PYTHONPATH}:$(pwd)/app/" python3.12 ./app/bot.py