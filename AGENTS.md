# Regras para uso de ferramentas neste projeto

## MCP Server
- SEMPRE que precisar acessar dados da API, use PRIMEIRO as ferramentas disponíveis no server MCP (api-sumarizacao)
- NÃO faça chamadas HTTP diretas (curl, etc.) para endpoints da API se houver ferramenta MCP correspondente
- Verifique as ferramentas disponíveis usando `mcp_list_tools` antes de acessar dados
- Use `mcp_call_tool` para executar as operações MCP

## Configuração MCP atual
- Server: api-sumarizacao
- URL: http://localhost:8000/mcp
- Transport: http
- Ferramentas disponíveis: filtros, listar_estacoes, listar_sensores, info_estacoes, info_sensores, raios_geojson, plotagem_mapa

## Fluxo correto para acessar dados:
1. Listar ferramentas MCP disponíveis: `mcp_list_tools`
2. Usar ferramenta MCP apropriada: `mcp_call_tool`
3. Apenas usar chamadas diretas se a operação não estiver disponível no MCP
