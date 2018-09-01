# What is this?

## Graphql application that allows you to use queries and mutations via web aiohttp server

## **Installation**

1. To run database (PostgreSQL) like docker service
    * **$ docker-compose up -d**
2. To run aiohttp server which has /graphql endpoint
    * **$ virtualenv -p python3 env && source env/bin/activate && python app/api.py**

3. To execute tests you need to call:
   * **$ cd ./app**
   * **$ python -m unittest tests**