import asyncio
import asyncpg


class DbConnectionConfig:
    POSTGRES_USER = 'graphql_user'
    POSTGRES_PASSWORD = '5l085x1vl4hk575qcr88p8yj4qr0a-j5f6'
    POSTGRES_DATABASE = 'graphql_db'


async def execute_query(query, *args, pg_method='execute', db_connection=None):
    if db_connection is None:
        db_connection = DbConnectionConfig()

    conn = await asyncpg.connect(
        user=db_connection.POSTGRES_USER,
        password=db_connection.POSTGRES_PASSWORD,
        database=db_connection.POSTGRES_DATABASE
    )

    result = await getattr(conn, pg_method)(query, *args)
    await conn.close()

    return result
