from aiohttp import web
from aiohttp_graphql import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor

from schema import schema

app = web.Application()
GraphQLView.attach(app, schema=schema, executor=AsyncioExecutor(), graphiql=True, pretty=True)

web.run_app(app)
