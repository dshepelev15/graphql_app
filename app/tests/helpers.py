from tests.data import (
    init_database,
    drop_database
)

async def reinitialize_database():
    '''This function will be called before each test'''

    await drop_database()
    account_ids, card_ids = await init_database()

    return account_ids, card_ids
