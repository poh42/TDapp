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

test:
	docker-compose -f docker-compose.dev.yml run --rm python -m unittest discover -s ./tests -t .

up-build: build
up-build: up

up-clean: rm
up-clean: up

up-build-clean: rm
up-build-clean: up-build
