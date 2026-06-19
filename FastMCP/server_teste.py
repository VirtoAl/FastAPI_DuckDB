from fastmcp import FastMCP, Context
from prefab_ui import PrefabApp
from prefab_ui.components import Column, Heading, Text, Badge, Row



mcp = FastMCP("Meu servidor de teste")


@mcp.tool
def summarize(content: str) -> str:
    return content[:50]

@mcp.tool
def bom_dia(nome: str) -> str:
    """
    Retorna uma mensagem de bom dia pro usuário
    """
    return f"Bom dia {nome}!"
@mcp.tool
def soma(x: int, y: int) -> str:
    """
    Retorna a soma de dois números
    """
    return f"A soma é: {x+y}"


# @mcp.tool()
# async def rimar(nome: str, ctx: Context) -> str:
#     """
#     Gera um pequeno elogio baseado se rima com o nome fornecido
#     """
#     result = await ctx.sample(f"Rime com o seguinte nome:\n\n{nome}")
#     return result.text or ""

# @mcp.tool(app=True)
# def bom_dia(nome: str) -> PrefabApp:
#     """
#     Tool utilizada para elogiar uma pessoa
#     """
#     with Column(gap=4, css_class="p-6") as view:
#         Heading(f"Bom dia {nome}!")
#         with Row(gap=4, align="center"):
#             Text("Status")
#             Badge("foi bom diado",variant="success")


#     return PrefabApp(view=view)

# @mcp.tool(app=True)
# def soma(x: int, y: int) -> PrefabApp:
#     """
#     Soma dois números0
#     """
#     with Column(gap=4, css_class="p-6") as view:
#         Heading(f"A soma é {x+y}!")
#         with Row(gap=4, align="center"):
#             Text("Status")
#             Badge("soma realizada", variant="success")

#     return PrefabApp(view=view)

# if __name__ == "__main__":
#     mcp.run(transport= "streamable-http", host="0.0.0.0",port="8000")