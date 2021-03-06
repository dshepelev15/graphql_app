import hashlib
from graphql import GraphQLError
from database import execute_query
from validation import (
    validate_code,
    validate_last4digit,
)


async def account_exists_by_logpass(login, password):
    password = hash_password(password)

    record = await execute_query('''
            SELECT id, login, password FROM account
            WHERE login = $1 AND password = $2''',
            login, password,
            pg_method='fetchrow'
        )
    is_exist = record is not None

    return is_exist, record


async def update_account_password(login, password, new_password):
    is_exist, record = await account_exists_by_logpass(login, password)
    if not is_exist:
        raise GraphQLError('Account does not exist')

    new_password = hash_password(new_password)

    res = await execute_query('''
        UPDATE account SET password = $2
        WHERE login = $1''',
        login, new_password
    )


async def update_card_details(**kwargs):
    if not kwargs:
        raise GraphQLError("Card's params can not be empty")
    id = kwargs['id']

    last4digit = kwargs.get('last4digit')
    if last4digit is not None:
        validate_last4digit(last4digit)

    code = kwargs.get('code')
    if code is not None:
        validate_code(code)

    # Particial update or full update
    query = '''
        UPDATE card SET {set_string}
        WHERE id = $1'''
    args = [id]
    set_column_list = []
    for k, v in kwargs.items():
        args.append(v)
        set_column_list.append('{} = ${}'.format(k, len(args)))

    set_string = ','.join(set_column_list)

    await execute_query(
        query.format(set_string=','.join(set_column_list)),
        *args
    )


def hash_password(password):
    return hashlib.md5(password.encode('utf-8')).hexdigest()
