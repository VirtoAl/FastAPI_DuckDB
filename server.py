from mcp.server.fastmcp import FastMCP
import requests
import sys

mcp = FastMCP("Meu servidor MCP")

@mcp.tool()
def busca_cep(cep: str) -> dict:
    """
    Docstring para busca_cep
    
    :param cep: Descrição
    :type cep: str
    :return: Descrição
    :rtype: dict
    """
    try:
        url = f"https://viacep.com.br/ws/{cep}/json"
        r = requests.get(url, timeout=5)
        data = r.json()
        if "erro" in data:
            return {"error": "CEP não encontrado"}
        return data
    except requests.RequestException as e:
        return {"error": str(e)}
    
# if __name__ == "__main__":
#     sys.stdout.reconfigure(line_buffering=True)
#     mcp.run()