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
	docker-compose -f up -d --remove-orphans

stop-prod:
	docker-compose -f stop

build-prod:
	docker-compose -f build

prod: stop-prod
prod: build-prod
prod: up-prod
