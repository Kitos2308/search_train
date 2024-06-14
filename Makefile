


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