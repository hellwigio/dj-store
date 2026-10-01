.PHONY: setup run migrate test check new
setup:
	python3 scripts/bootstrap.py
	uv sync --locked
	uv run python manage.py migrate
run:
	uv run python manage.py runserver
migrate:
	uv run python manage.py migrate
test:
	uv run pytest
check:
	uv run ruff check .
	uv run ruff format --check .
	uv run python manage.py check
	uv run python manage.py makemigrations --check --dry-run
new:
	python3 scripts/new_project.py "$(DEST)"
