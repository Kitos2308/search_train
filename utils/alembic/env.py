from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, text
import sqlalchemy
from alembic import context
from search.settings import settings
import sys

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

config.set_main_option(
    "sqlalchemy.url",
    "postgresql://%s:%s@%s:%s/%s" % (
        settings.DB_USER,
        settings.DB_PASS,
        settings.DB_HOST,
        settings.DB_PORT,
        settings.DB_NAME
    )
)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)  # type: ignore

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata
target_metadata.schema = settings.DB_SCHEMA

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        include_schemas=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),  # type: ignore
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    db_schema = settings.DB_SCHEMA
    with connectable.connect() as connection:
        if settings.ENVIRONMENT == 'test':
            # В тестовом окружении создаем схему автоматически
            connection.execute(sqlalchemy.schema.CreateSchema(db_schema, if_not_exists=True))

        connection.execute(text(f'SET SEARCH_PATH TO "{db_schema}"'))
        connection.commit()
        connection.dialect.default_schema_name = db_schema

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

    """       
    Для локального окружения, если хочется запускать тесты в отдельной схеме БД
    то нужно в .env
    TEST_DB_SCHEMA=<test_schema_name>
    """
    if '--autogenerate' not in sys.argv and settings.TEST_DB_SCHEMA:
        print('')
        print(f'TEST_DB_SCHEMA is {settings.TEST_DB_SCHEMA}')
        test_db_schema = settings.TEST_DB_SCHEMA
        with connectable.connect() as connection:
            connection.execute(text(f'SET SEARCH_PATH TO "{test_db_schema}"'))
            connection.commit()
            connection.dialect.default_schema_name = test_db_schema

            context.configure(
                connection=connection,
                target_metadata=target_metadata,
            )

            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
