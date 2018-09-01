import asyncpg
import graphene as g
from graphql import GraphQLError

from database import execute_query
from util import account_exists_by_logpass
from utils import (
    update_account_password,
    update_card_details,
)


### QUERIES
class Account(g.ObjectType):
    id = g.ID()
    login = g.String()


class Card(g.ObjectType):
    id = g.ID()
    last4digit = g.String()
    code = g.String()
    type = g.String()


class Query(g.ObjectType):
    account = g.Field(Account, login=g.String(required=True), password=g.String(required=True))
    cards = g.List(Card, account_id=g.Int(required=True), card_id=g.Int())

    async def resolve_account(self, info, login, password):
        is_exist, record = await account_exists_by_logpass(login, password)
        if not is_exist:
            raise GraphQLError('Account does not exist')

        return Account(id=record['id'], login=record['login'])

    async def resolve_cards(self, info, account_id, card_id=None):
        query = '''
            SELECT id, last4digit, code, type FROM card
            WHERE account_id = $1 {unique_card}
        '''
        args = [account_id]
        unique_card = ''
        if card_id is not None:
            unique_card = 'AND card_id = $2'
            args.append(card_id)

        records = await execute_query(query.format(unique_card=unique_card),
            *args,
            pg_method='fetch'
        )

        return [
            Card(id=record['id'], last4digit=record['last4digit'], code=record['code'], type=record['type'])
            for record in records
        ]


### MUTATIONS
class CreateAccount(g.Mutation):
    class Arguments:
        login = g.String(required=True)
        password = g.String(required=True)

    id = g.ID()

    async def mutate(self, info, login, password):
        try:
            id = await execute_query('''
                INSERT INTO account (login, password)
                VALUES ($1, $2)
                RETURNING id''',
                login, password,
                pg_method='fetchval'
            )
        except asyncpg.exceptions.UniqueViolationError:
            raise GraphQLError('That login already exists')

        return CreateAccount(id=id)


class UpdateAccountPassword(g.Mutation):
    class Arguments:
        login = g.String(required=True)
        password = g.String(required=True)
        new_password = g.String(required=True)

    success = g.Boolean()

    async def mutate(self, info, login, password, new_password):
        update_account_password(login, password, new_password)

        return UpdateAccountPassword(success=True)


class DeleteAccount(g.Mutation):
    class Arguments:
        id = g.Int(required=True)

    success = g.Boolean()

    async def mutate(self, info, id):
        await execute_query('''
            DELETE FROM account
            WHERE id = $1''',
            id)

        return DeleteAccount(success=True)


class CreateCard(g.Mutation):
    class Arguments:
        account_id = g.Int(required=True)
        last4digit = g.String(required=True)
        code = g.String(required=True)
        type = g.String(required=True)

    id = g.ID()

    async def mutate(self, info, account_id, last4digit, code, type):
        validate_card_params(last4digit, code)

        row = await execute_query('''
            SELECT id FROM account
            WHERE id = $1''',
            account_id,
            pg_method='fetchrow')

        if row is None:
            raise GraphQLError('Account does not exist')

        id = await execute_query('''
                INSERT INTO card (account_id, last4digit, code, type)
                VALUES ($1, $2, $3, $4)
                RETURNING id
                ''',
                account_id, last4digit, code, type,
                pg_method='fetchval'
            )

        return CreateCard(id=id)


class UpdateCard(g.Mutation):
    class Arguments:
        id = g.Int(required=True)
        account_id = g.Int()
        last4digit = g.String()
        code = g.String()
        type = g.String()

    success = g.Boolean()

    async def mutate(self, info, id, **kwargs):
        update_card_details(id=id, **kwargs)

        return UpdateCard(success=True)


class DeleteCard(g.Mutation):
    class Arguments:
        id = g.Int(required=True)

    success = g.Boolean()

    async def mutate(self, info, id):
        await execute_query('''
            DELETE FROM card
            WHERE id = $1''',
            id)

        return DeleteCard(success=True)


# Inputs with all required True
class AccountInput(g.InputObjectType):
    login = g.String(required=True)
    password = g.String(required=True)
    new_password = g.String(required=True)


class CardInput(g.InputObjectType):
    id = g.Int(required=True)
    last4digit = g.String(required=True)
    code = g.String(required=True)
    type = g.String(required=True)


class UpdateFullCard(g.Mutation):
    class Arguments:
        account = AccountInput(required=True)
        card = CardInput(required=True)

    success = g.Boolean()

    async def mutate(self, info, account, card):
        update_account_password(account.login, account.password, account.new_password)
        update_card_details(id=card.id, last4digit=card.last4digit, code=card.code, type=card.type)

        return UpdateFullCard(success=True)


class Mutation(g.ObjectType):
    create_account = CreateAccount.Field()
    update_account_password = UpdateAccountPassword.Field()
    delete_account = DeleteAccount.Field()

    create_card = CreateCard.Field()
    update_card = UpdateCard.Field()
    delete_card = DeleteCard.Field()

    # just this mutation is needed
    update_full_card = UpdateFullCard.Field()


schema = g.Schema(query=Query, mutation=Mutation)
