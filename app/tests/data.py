import asyncpg
from database import (
    ConnectionConfig,
    execute_query
)


class DbTestConnectionConfig(ConnectionConfig):
    POSTGRES_USER = 'graphql_test'
    POSTGRES_PASSWORD = '0dexjkfd2ads1a5c6514b4dec'
    POSTGRES_DATABASE = 'graphql_db_test'


def test_execute_query(*args, **kwargs):
    return execute_query(*args, **kwargs, db_connection=DbTestConnectionConfig)


async def init_database():
    account_values = [
        ('account_number1', 'right_password_here'),
        ('account_number2', 'password_again'),
        ('test_login', 'test_password')
    ]
    account_ids = [await test_execute_query('''
        INSERT INTO account (login, password)
        VALUES ($1, $2)
        RETURNING id''',
        *account,
        pg_method='fetchval')
        for account in account_values
    ]

    card_values = [
        ('1234', '123', 'this is type of card', account_ids[0]),
        ('2345', '987', 'this is type of card', account_ids[0]),
        ('3456', '456', 'this is type of card', account_ids[0]),
        ('1357', '187', 'second account', account_ids[1]),
        ('8643', '356', 'second account', account_ids[1]),
        ('5432', '777', '3 account', account_ids[2]),
        ('1234', '943', '3 account', account_ids[2]),
    ]

    card_ids = [await test_execute_query('''
        INSERT INTO card (last4digit, code, type, account_id)
        VALUES ($1, $2, $3, $4)
        RETURNING id''',
        *card,
        pg_method='fetchval')
        for card in card_values
    ]

    return account_ids, card_ids


async def drop_database():
    await test_execute_query('DELETE FROM card')
    await test_execute_query('DELETE FROM account')
