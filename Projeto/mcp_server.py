from mcp.server.fastmcp import FastMCP

mcp = FastMCP("MeuServidorMCP")

@mcp.tool()
def minha_funcao() -> str:
    """Vamo ver se isso aqui funciona dessa vez"""
    url = "https://modelcontextprotocol.io/docs/getting-started/intro/"
    resultado = f"Para aprender mais sobre MCP, acesse o site: {url}"
    return resultado

if __name__ == "__main__":
    mcp.run()