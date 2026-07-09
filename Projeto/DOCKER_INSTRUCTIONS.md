# Instruções para uso do Docker com volumes

## Construção da imagem

A imagem agora é otimizada para não incluir os dados grandes (dadosSimepar):

```bash
docker build -t fastapi-duckdb .
```

**Estimativa de espaço necessário:**
- Antes: ~27-30GB (incluindo 25GB de dados)
- Agora: ~516KB (apenas código + dependências) + ~2-3GB (imagem base Python)

## Execução do container com volume

Para rodar o container montando os dados externamente:

```bash
docker run -v $(pwd)/dadosSimepar:/app/dadosSimepar -v $(pwd)/dados_estacao.duckdb:/app/dados_estacao.duckdb -v $(pwd)/geometria_area_raios.geojson:/app/geometria_area_raios.geojson -v $(pwd)/geometria_estacoes.geojson:/app/geometria_estacoes.geojson -v $(pwd)/geometria_raios.geojson:/app/geometria_raios.geojson -p 8000:8000 fastapi-duckdb
```

**Explicação:**
- `-v $(pwd)/dadosSimepar:/app/dadosSimepar` - Monta o diretório local `dadosSimepar` em `/app/dadosSimepar` dentro do container
- `-v $(pwd)/dados_estacao.duckdb:/app/dados_estacao.duckdb` - Monta o banco de dados DuckDB
- `-v $(pwd)/geometria_*.geojson:/app/geometria_*.geojson` - Monta os arquivos GeoJSON
- `-p 8000:8000` - Mapeia a porta 8000 do container para a porta 8000 do host
- `fastapi-duckdb` - Nome da imagem

**Simplificado (montando todo o diretório do projeto):**
```bash
docker run -v $(pwd):/app -p 8000:8000 fastapi-duckdb
```

## Vantagens desta abordagem

1. **Economia de espaço:** A imagem Docker não inclui os 25GB de dados
2. **Atualização em tempo real:** Alterações nos dados são refletidas imediatamente no container
3. **Persistência:** Dados permanecem no host mesmo se o container for removido
4. **Build mais rápido:** Não precisa copiar 25GB durante o build

## Outras opções de volume

### Bind mount específico:
```bash
docker run -v /caminho/completo/para/dadosSimepar:/app/dadosSimepar -p 8000:8000 fastapi-duckdb
```

### Volume gerenciado pelo Docker:
```bash
docker volume create dados-simepar
docker run -v dados-simepar:/app/dadosSimepar -p 8000:8000 fastapi-duckdb
```

## Verificação do espaço

Antes de construir, verifique o espaço disponível:

```bash
df -h /
```

Espaço necessário aproximado: 2-3GB (muito menor que os 27-30GB anteriores)

## Integração com MCP Server

O container inclui um servidor MCP acessível no endpoint `/mcp` na porta 8000. Para configurar o Devin CLI para usar este servidor:

1. Execute o container conforme instruções acima
2. Configure o arquivo `~/.config/devin/mcp_servers.json`:
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

Para instruções detalhadas, consulte o arquivo `MCP_SETUP.md`.
