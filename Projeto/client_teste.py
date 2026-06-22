import asyncio
from fastmcp import Client


async def main():
    async with Client("http://127.0.0.1:8001/mcp") as client:
    # async with Client("server_teste.py") as client:

        resultado = await client.call_tool(
            "bom_dia",
            {"nome": "Virto"}
        )

        print(resultado)

        resultado = await client.call_tool(
            "pratogit",
            {"x": 4, "y": 12}
        )

        print(resultado)

        resultado = await client.call_tool(
            "summarize",
            {"content": "texto muito grande..."}
        )

        print(resultado)

        resultado = await client.call_tool(
            "id",
            {"id": 4}
        )

        print(resultado)

asyncio.run(main())