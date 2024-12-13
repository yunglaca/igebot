#!make

path:
	export PYTHONPATH="${PYTHONPATH}:/home/laca/test-async-alembic/app/"

.PHONY: .env
.env:
	@if [ ! -f ./.env ]; then \
		echo "Please create and fill .env file!" && exit 1; \
	fi

include .env

update_deps:
	echo -e "\033[1;34mStep 2: Installin pip-tools ...\033[0m"
	python3.12 -m pip install --upgrade pip setuptools wheel
	python3.12 -m pip install --upgrade pip-tools
	echo -e "\033[1;34mStep 3: Removing old deps ...\033[0m"
	rm ./requirements/requirements*.txt || true
	echo -e "\033[1;34mStep 4: Creating requirements.txt ...\033[0m"
	pip-compile ./requirements/requirements.in --output-file ./requirements/requirements.txt
	echo -e "\033[1;34mStep 5: Creating requirements-dev.txt ...\033[0m"
	pip-compile ./requirements/requirements-dev.in --output-file ./requirements/requirements-dev.txt
	
.PHONY: venv
venv:
	rm -rf venv
	python3.12 -m venv ./venv
#	. venv/bin/activate; pip install -r requirements/requirements.txt -r requirements/requirements-dev.txt -e .
	. venv/bin/activate; pip install -r requirements.txt

init_db: | .env
	sudo -u postgres psql -c 'create database ${DB_NAME};' || true
#   sudo -u postgres psql -d ${DB_NAME} -c 'create schema ${DB_SCHEMA};' || true
	sudo -u postgres psql -d ${DB_NAME} -c "create role ${DB_USER} with password '${DB_PASS}';" || true
	sudo -u postgres psql -d ${DB_NAME} -c "alter role ${DB_USER} superuser login;" || true
	sudo -u postgres psql -d ${DB_NAME} -c 'grant all privileges on database ${DB_NAME} to ${DB_USER};' || true
	sudo -u postgres psql -d ${DB_NAME} -c 'grant all privileges on schema public to ${DB_USER};' || true
	. venv/bin/activate; alembic upgrade head

start_bot:
	PYTHONPATH="${PYTHONPATH}:/home/laca/test-async-alembic/app/" python3.12 ./app/bot.py