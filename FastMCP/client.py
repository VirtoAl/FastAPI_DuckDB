import asyncio

from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession


async def main():
    async with streamablehttp_client(
        "http://localhost:8001/mcp"
    ) as (read_stream, write_stream, _):
        async with ClientSession(
            read_stream,
            write_stream
        ) as session:

            await session.initialize()

            result = await session.call_tool(
    "busca_cep",
    {"cep": "01001000"}
)
            print(result)

asyncio.run(main())