import asyncio
import aiounittest

from tests.data import test_execute_query
from tests.helpers import reinitialize_database
from schema import schema
from utils import account_exists_by_logpass


class MutationTestCase(aiounittest.AsyncTestCase):
    def get_event_loop(self):
        loop = asyncio.get_event_loop()
        self.account_ids, self.card_ids = loop.run_until_complete(reinitialize_database())

        return None

    async def test_create_account(self):
        before = await self._select_account_ids()


        query = '''
            mutation {
                createAccount(login: "helloworld", password: "password") {
                    id
                }
            }
        '''

        res = await schema.execute(query, return_promise=True)

        account_id = res.data['createAccount']['id']
        self.assertIsNone(res.errors)
        self.assertTrue(type(account_id), int)

        after = await self._select_account_ids()
        self.assertEquals(len(before) + 1, len(after))
        self.assertIn(account_id, after)
        self.assertNotIn(account_id, before)

    async def _select_account_ids(self):
        accounts = await test_execute_query('SELECT id FROM account', pg_method='fetch')
        ids = [account['id'] for account in accounts]

        return ids

    async def test_create_account_login_already_exists(self):
        query = '''
            mutation {
                createAccount(login: "test_login", password: "password") {
                    id
                }
            }
        '''

        res = await schema.execute(query, return_promise=True)

        self.assertIsNotNone(res.errors)
        self.assertEquals(res.errors[0].message, "That login already exists")

    async def test_create_account_login_less_min_length(self):
        query = '''
            mutation {
                createAccount(login: "log", password: "password") {
                    id
                }
            }
        '''

        res = await schema.execute(query, return_promise=True)

        self.assertIsNotNone(res.errors)
        self.assertEquals(res.errors[0].message, "login length error")

    async def test_create_account_login_more_max_length(self):
        query = '''
            mutation {
                createAccount(login: "thisisverybigloginaccountname1234567890thisisverybigloginaccountname1234567890thisisverybigloginaccountname1234567890thisisverybigloginaccountname1234567890", password: "password") {
                    id
                }
            }
        '''

        res = await schema.execute(query, return_promise=True)

        self.assertIsNotNone(res.errors)
        self.assertEquals(res.errors[0].message, "login length error")

    async def test_delete_account(self):
        before = await self._select_account_ids()

        id_for_deletion = self.account_ids[0]

        query = '''
            mutation {
                deleteAccount(id: %d) {
                    id
                }
            }
        ''' % id_for_deletion

        res = await schema.execute(query, return_promise=True)

        account_id = res.data['deleteAccount']['id']
        self.assertIsNone(res.errors)
        self.assertTrue(type(account_id), int)

        after = await self._select_account_ids()
        self.assertEquals(len(before), len(after) + 1)
        self.assertIn(account_id, before)
        self.assertNotIn(account_id, after)

    async def test_update_account_password(self):
        login, password = 'account_number1', 'right_password_here'
        new_password = 'new_password'

        query = '''
            mutation {
                updateAccountPassword(login: "%s", password: "%s", newPassword: "%s") {
                    success
                }
            }''' % (login, password, new_password)

        res = await schema.execute(query, return_promise=True)

        self.assertIsNone(res.errors)
        self.assertTrue(res.data['updateAccountPassword']['success'])

        is_exist, _ = await account_exists_by_logpass(login, password)
        self.assertFalse(is_exist)
        is_exist, _ = await account_exists_by_logpass(login, new_password)
        self.assertTrue(is_exist)

    async def test_create_card(self):
        last4digit = '2143'
        code = '123'
        type_value = 'any type here'
        account_id = self.account_ids[0]
        before = await self._select_card_ids()

        query = '''
            mutation {
                createCard(last4digit: "%s", code: "%s", type: "%s", accountId: %d) {
                    id
                }
            }''' % (last4digit, code, type_value, account_id)

        res = await schema.execute(query, return_promise=True)

        card_id = res.data['createCard']['id']
        self.assertIsNone(res.errors)
        self.assertEquals(type(card_id), int)

        after = await self._select_card_ids()
        self.assertEquals(len(before) + 1, len(after))
        self.assertIn(card_id, after)
        self.assertNotIn(card_id, before)

    async def _select_card_ids(self):
        cards = await test_execute_query('SELECT id FROM card', pg_method='fetch')
        ids = [card['id'] for card in cards]

        return ids

    async def test_create_card_last4digit_digital_validation_error(self):
        last4digit = 'home'

        code = '123'
        type = 'any type here'
        account_id = self.account_ids[0]
        before = await self._select_card_ids()

        query = '''
            mutation {
                createCard(last4digit: "%s", code: "%s", type: "%s", accountId: %d) {
                    id
                }
            }''' % (last4digit, code, type, account_id)

        res = await schema.execute(query, return_promise=True)

        self.assertIsNotNone(res.errors)
        self.assertEquals(res.errors[0].message, 'last4digit contains no digit character(s)')

    async def test_create_card_last4digit_length_validation_error(self):
        last4digit = '123456789'

        code = '123'
        type = 'any type here'
        account_id = self.account_ids[0]
        before = await self._select_card_ids()

        query = '''
            mutation {
                createCard(last4digit: "%s", code: "%s", type: "%s", accountId: %d) {
                    id
                }
            }''' % (last4digit, code, type, account_id)

        res = await schema.execute(query, return_promise=True)

        self.assertIsNotNone(res.errors)
        self.assertEquals(res.errors[0].message, 'last4digit length error')

    async def test_create_card_code_digital_validation_error(self):
        code = 'c++'

        last4digit = '5264'
        type = 'any type here'
        account_id = self.account_ids[0]
        before = await self._select_card_ids()

        query = '''
            mutation {
                createCard(last4digit: "%s", code: "%s", type: "%s", accountId: %d) {
                    id
                }
            }''' % (last4digit, code, type, account_id)

        res = await schema.execute(query, return_promise=True)

        self.assertIsNotNone(res.errors)
        self.assertEquals(res.errors[0].message, 'code contains no digit character(s)')

    async def test_create_card_code_length_validation_error(self):
        code = '16789343'

        last4digit = '1234'
        type = 'any type here'
        account_id = self.account_ids[0]
        before = await self._select_card_ids()

        query = '''
            mutation {
                createCard(last4digit: "%s", code: "%s", type: "%s", accountId: %d) {
                    id
                }
            }''' % (last4digit, code, type, account_id)

        res = await schema.execute(query, return_promise=True)

        self.assertIsNotNone(res.errors)
        self.assertEquals(res.errors[0].message, 'code length error')

    async def test_delete_card(self):
        before = await self._select_card_ids()
        id_for_deletion = self.card_ids[0]

        query = '''
            mutation {
                deleteCard(id: %d) {
                    id
                    success
                }
            }
        ''' % id_for_deletion

        res = await schema.execute(query, return_promise=True)

        card_id = res.data['deleteCard']['id']
        self.assertTrue(res.data['deleteCard']['success'])
        self.assertIsNone(res.errors)
        self.assertTrue(type(card_id), int)

        after = await self._select_card_ids()
        self.assertEquals(len(before), len(after) + 1)
        self.assertIn(card_id, before)
        self.assertNotIn(card_id, after)

    async def test_update_entire_card(self):
        card_id = self.card_ids[0]
        account_id = self.account_ids[-1]

        last4digit = '1234'
        code = '3431'
        type_value = 'type of card'

        before = await self._select_card_ids()

        query = '''
            mutation {
                updateCard(last4digit: "%s", code: "%s", type: "%s", accountId: %d, id: %d) {
                    id
                    success
                }
            }''' % (last4digit, code, type_value, account_id, card_id)

        res = await schema.execute(query, return_promise=True)

        card_id = res.data['updateCard']['id']
        self.assertIsNone(res.errors)
        self.assertEquals(type(card_id), int)

        after = await self._select_card_ids()
        self.assertEquals(len(before), len(after))
        self.assertIn(card_id, after)
        self.assertIn(card_id, before)

    async def test_particial_update_card(self):
        card_id = self.card_ids[0]
        account_id = self.account_ids[-1]

        code = '362'

        before = await self._select_card_ids()

        query = '''
            mutation {
                updateCard(code: "%s", id: %d) {
                    id
                    success
                }
            }''' % (code, card_id)

        res = await schema.execute(query, return_promise=True)

        card_id = res.data['updateCard']['id']
        self.assertIsNone(res.errors)
        self.assertEquals(type(card_id), int)

        after = await self._select_card_ids()
        self.assertEquals(len(before), len(after))
        self.assertIn(card_id, after)
        self.assertIn(card_id, before)

    async def test_update_card_last4digit_digital_validation_error(self):
        card_id = self.card_ids[0]
        account_id = self.account_ids[-1]

        last4digit = 'good'
        code = '343'
        type_value = 'type of card'

        before = await self._select_card_ids()

        query = '''
            mutation {
                updateCard(last4digit: "%s", code: "%s", type: "%s", accountId: %d, id: %d) {
                    id
                    success
                }
            }''' % (last4digit, code, type_value, account_id, card_id)

        res = await schema.execute(query, return_promise=True)

        self.assertIsNotNone(res.errors)
        self.assertEquals(res.errors[0].message, 'last4digit contains no digit character(s)')

    async def test_update_full_card(self):
        variables = {
            'login': 'account_number2',
            'password': 'password_again',
            'newPassword': 'newpassword_from_again',
            'id': self.card_ids[0],
            'code': '542',
            'last4digit': '6317',
            'type': 'type of card,'
        }

        query = '''
            mutation {
                updateFullCard(
                    account: {login: "%s", password: "%s", newPassword: "%s"},
                    card: {id: %d, code: "%s", last4digit: "%s", type: "%s"}) {
                    success
                }
        }''' % (
            variables['login'], variables['password'], variables['newPassword'],
            variables['id'], variables['code'], variables['last4digit'], variables['type']
        )

        # query = '''
        #     mutation {
        #         updateFullCard(
        #             account: {$login: Str!, $password: Str!, $newPassword: Str!},
        #             card: {$id: Int!, $code: Str!, $last4digit: Str!, $type: Str!}) {
        #             success
        #         }
        # }'''

        res = await schema.execute(query, return_promise=True)
        self.assertIsNone(res.errors)
        self.assertTrue(res.data['updateFullCard']['success'])
