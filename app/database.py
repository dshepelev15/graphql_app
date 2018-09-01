import asyncio
import asyncpg

POSTGRES_USER = 'graphql_user'
POSTGRES_PASSWORD = '5l085x1vl4hk575qcr88p8yj4qr0a-j5f6'
POSTGRES_DATABASE = 'graphql_db'


async def execute_query(query, *args, pg_method='execute'):
    conn = await asyncpg.connect(
        user=POSTGRES_USER, password=POSTGRES_PASSWORD, database=POSTGRES_DATABASE
    )

    result = await getattr(conn, pg_method)(query, *args)
    await conn.close()

    return result
