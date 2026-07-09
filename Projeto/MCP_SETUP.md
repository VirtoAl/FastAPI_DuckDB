# Configuração do MCP Server com Docker

## Visão Geral

O servidor MCP está integrado na aplicação FastAPI através do `fastapi-mcp` e é acessível no endpoint `/mcp` da mesma porta (8000) da aplicação.

## Configuração do Docker

### 1. Construir a imagem

```bash
docker build -t fastapi-duckdb .
```

### 2. Executar o container

```bash
docker run -v $(pwd)/dadosSimepar:/app/dadosSimepar -v $(pwd)/dados_estacao.duckdb:/app/dados_estacao.duckdb -v $(pwd)/geometria_area_raios.geojson:/app/geometria_area_raios.geojson -v $(pwd)/geometria_estacoes.geojson:/app/geometria_estacoes.geojson -v $(pwd)/geometria_raios.geojson:/app/geometria_raios.geojson -p 8000:8000 fastapi-duckdb
```

**Ou simplificado (monta todo o diretório do projeto):**
```bash
docker run -v $(pwd):/app -p 8000:8000 fastapi-duckdb
```

## Configuração do Devin CLI (Host)

### 1. Criar arquivo de configuração MCP

Crie ou edite o arquivo `~/.config/devin/mcp_servers.json`:

```bash
mkdir -p ~/.config/devin
nano ~/.config/devin/mcp_servers.json
```

### 2. Adicionar configuração do servidor

```json
{
  "mcpServers": {
    "duckdb-api": {
      "url": "http://localhost:8000/mcp",
      "transport": "http"
    }
  }
}
```

### 3. Verificar configuração

Depois de configurar, você pode verificar se o Devin CLI está reconhecendo o servidor MCP listando as ferramentas disponíveis:

```bash
devin mcp list-tools
```

Isso deve mostrar as ferramentas disponíveis no servidor:
- `filtros`
- `listar_estacoes`
- `listar_sensores`
- `info_estacoes`
- `info_sensores`
- `raios_geojson`
- `plotagem_mapa`

## Uso com Devin CLI

Depois de configurado, você pode usar as ferramentas MCP nas suas sessões do Devin CLI. O sistema automaticamente usará as ferramentas disponíveis no servidor MCP quando apropriado.

Exemplo de como o sistema funcionará:
1. O Devin CLI detecta que há um servidor MCP configurado
2. Quando você pede dados de estações ou sensores, o Devin usa as ferramentas MCP
3. As requisições vão para `http://localhost:8000/mcp`
4. O container Docker processa a requisição e retorna os dados

## Troubleshooting

### Verificar se o container está rodando
```bash
docker ps
```

### Verificar logs do container
```bash
docker logs <container_id>
```

### Testar endpoint MCP diretamente
```bash
curl http://localhost:8000/mcp
```

### Verificar se a porta está acessível
```bash
netstat -tlnp | grep 8000
```

### Recompor configuração MCP se necessário
Se precisar atualizar a configuração, edite o arquivo `~/.config/devin/mcp_servers.json` e reinicie sua sessão do Devin CLI.