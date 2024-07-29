


compose.up:
	docker compose up -d

compose.down:
	docker compose down -v


migrate.gen:
	alembic revision --autogenerate

migrate.up:
	alembic --raiseerr upgrade head

migrate.down:
	alembic --raiseerr downgrade -1

migrate.autopep:
	autopep8 --in-place alembic/versions/*.py

fill:
	poetry run python fill_source_data.py

indexing:
	poetry run python -m app.elasticsearch_draft


run.local:
	uvicorn app.api.fastapi_app:app --reload --env-file="./.env" --host 127.0.0.1

cli.fill:
	 python -m app.cli.typer_app indexing fill-data-postgres


cli.reindex:
	python -m app.cli.typer_app indexing start-full-reindex

cli.help:
	python -m app.cli.typer_app indexing --help