.PHONY: lint test docker-build docker-push

lint:
	poetry run ruff check src tests
	poetry run black --check src tests
	poetry run isort --check-only src tests
	poetry run codespell src tests docs
	poetry run mypy src

test:
	poetry run pytest -q --tb=short

docker-build:
	docker compose -f docker/docker-compose.yml build

docker-push:
	docker compose -f docker/docker-compose.yml push
