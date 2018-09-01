import asyncio
import aiounittest

from tests.helpers import reinitialize_database
from schema import schema


class QueryTestCase(aiounittest.AsyncTestCase):
    def get_event_loop(self):
        loop = asyncio.get_event_loop()
        self.account_ids, self.card_ids = loop.run_until_complete(reinitialize_database())

        return None

    async def test_account_does_not_exist(self):
        query = '''
            query {
                account(login: "something", password: "some wrong password") {
                    id
                    login
                }
            }
        '''

        res = await schema.execute(query, return_promise=True)

        self.assertIsNotNone(res.errors)
        self.assertIsNone(res.data.get('account'))
        self.assertEquals(res.errors[0].message, "Account does not exist")

    async def test_missing_password_parameter(self):
        query = '''
            query {
                account(login: "something") {
                    id
                }
            }
        '''

        res = await schema.execute(query, return_promise=True)

        self.assertIsNone(res.data)
        self.assertIsNotNone(res.errors)
        self.assertEquals(str(res.errors[0].message), 'Field "account" argument "password" of type "String!" is required but not provided.')

    async def test_missing_login_parameter(self):
        query = '''
            query {
                account(password: "something") {
                    id
                }
            }
        '''

        res = await schema.execute(query, return_promise=True)

        self.assertIsNone(res.data)
        self.assertIsNotNone(res.errors)
        self.assertEquals(res.errors[0].message, 'Field "account" argument "login" of type "String!" is required but not provided.')

    async def test_account_id_field_integer_matching(self):
        query = '''
            query {
                account(login: "account_number1", password: "right_password_here") {
                    id
                    login
                }
            }
        '''

        res = await schema.execute(query, return_promise=True)

        self.assertIsNone(res.errors)
        self.assertEquals(res.data['account']['id'], self.account_ids[0])

    async def test_account_login_and_password_matching(self):
        login, password = 'account_number1', 'right_password_here'
        query = '''
            query {
                account(login: "%s", password: "%s") {
                    login
                    password
                }
            }
        ''' % (login, password)

        res = await schema.execute(query, return_promise=True)

        self.assertIsNone(res.errors)

        account = res.data['account']
        self.assertEquals(account['login'], login)
        self.assertEquals(account['password'], password)

    async def test_cards_retrieving_by_integer_account_id(self):
        account_id = self.account_ids[0]
        N = 3 # cards for account

        query = '''
            query {
                cards(accountId: %d) {
                    id
                }
            }
        ''' % account_id

        res = await schema.execute(query, return_promise=True)

        self.assertIsNone(res.errors)

        cards = res.data['cards']
        self.assertEqual(len(cards), N)
        [self.assertIn(card['id'], self.card_ids) for card in cards]

    async def test_error_cards_retrieving_by_string_account_id(self):
        account_id = self.account_ids[0]
        query = '''
            query {
                cards(accountId: "%s") {
                    id
                }
            }
        ''' % account_id

        res = await schema.execute(query, return_promise=True)

        self.assertIsNotNone(res.errors)
        self.assertTrue(res.errors[0].message.startswith('Argument "accountId" has invalid value'))

    async def test_card_retrieving_by_account_id_anc_card_id(self):
        account_id = self.account_ids[0]
        card_id = self.card_ids[0]
        query = '''
            query {
                cards(accountId: %d, cardId: %d) {
                    id
                    last4digit
                    code
                    type
                }
            }
        ''' % (account_id, card_id)

        res = await schema.execute(query, return_promise=True)

        self.assertIsNone(res.errors)

        cards = res.data['cards']
        self.assertEqual(len(cards), 1)
        self.assertIn(cards[0]['id'], self.card_ids)

        self.assertEquals(type(cards[0]['id']), int)
        self.assertEquals(type(cards[0]['last4digit']), str)
        self.assertEquals(type(cards[0]['code']), str)
        self.assertEquals(type(cards[0]['type']), str)
