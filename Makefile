build:
	docker-compose -f docker-compose.dev.yml build

up:
	docker-compose -f docker-compose.dev.yml up --remove-orphans

rm:
	docker-compose -f docker-compose.dev.yml rm

down:
	docker-compose -f docker-compose.dev.yml down

bash:
	docker-compose -f docker-compose.dev.yml run --rm app /bin/ash

create_fixtures:
	docker-compose -f docker-compose.dev.yml run --rm app flask create_fixtures

send_sms_upcoming_challenges:
	docker-compose -f docker-compose.dev.yml run --rm app flask send_sms_upcoming_challenges


run_migrations:
	docker-compose -f docker-compose.dev.yml run --rm app flask db upgrade

test:
	docker-compose -f docker-compose.test.yml run --rm app python -m unittest discover -s ./tests -t .

up-build: build
up-build: up

up-clean: rm
up-clean: up

up-build-clean: rm
up-build-clean: up-build

up-prod:
	docker-compose up -d --remove-orphans

stop-prod:
	docker-compose stop

build-prod:
	docker-compose build

prod: stop-prod
prod: build-prod
prod: up-prod
