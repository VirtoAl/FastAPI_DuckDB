# Devin CLI com Docker - Integração MCP

Projeto de integração do Devin CLI com Docker para desenvolvimento com MCP (Model Context Protocol).

## 🚀 Quick Start

```bash
# 1. Iniciar os serviços
./devin-setup.sh

# 2. Autenticar (obrigatório)
./auth-helper.sh

# 3. Usar o Devin CLI
docker exec -it devin-mcp-client bash
cd /workspace/Projeto
devin --sandbox --permission-mode autonomous
```

## 📋 Estrutura do Projeto

```
Projeto/
├── docker-compose.yml          # Orquestração dos containers
├── Dockerfile                   # Dockerfile da API
├── Dockerfile.devin            # Dockerfile do Devin CLI com configuração embutida
├── devin-setup.sh             # Script de setup automático
├── auth-helper.sh             # Helper para autenticação
├── DEVIN_DOCKER_GUIDE.md      # Guia completo de uso
├── DISTRIBUTION.md            # Guia de distribuição da imagem
└── README.md                  # Este arquivo
```

## 🔐 Autenticação

**O Devin CLI requer autenticação obrigatória.** Use o helper:

```bash
./auth-helper.sh
```

Ou manualmente:

```bash
docker exec -it devin-mcp-client bash
devin auth login
```

As credenciais são persistidas no volume Docker `devin-credentials`, então você só precisa autenticar uma vez.

## 🔧 Configuração

A configuração está **embutida na imagem Docker**:

- **Permissões**: Leitura completa, escrita no workspace, comandos Docker/Git/MCP
- **Sandbox**: Domínios permitidos (localhost, api), modo de rede completo
- **MCP**: Servidor `api-sumarizacao` configurado em `http://api:8000/mcp`

Não é necessário manter arquivos de configuração localmente.

## 📦 Distribuição

Para distribuir a imagem:

```bash
# Build e tag
docker build -f Dockerfile.devin -t seu-usuario/devin-mcp-client:latest .

# Push para Docker Hub
docker push seu-usuario/devin-mcp-client:latest
```

Veja [DISTRIBUTION.md](DISTRIBUTION.md) para mais detalhes.

## 🧪 Usando MCP

Dentro do Devin CLI:

```bash
# Listar ferramentas MCP disponíveis
/mcp_list_tools

# Usar ferramenta específica
/mcp_call_tool server_name="api-sumarizacao" tool_name="listar_estacoes"
```

## 🛠️ Solução de Problemas

### Container não inicia

```bash
docker-compose logs devin
```

### MCP não conecta

```bash
docker exec devin-mcp-client curl http://api:8000/mcp
```

### Autenticação falha

```bash
docker exec devin-mcp-client devin auth status
```

### Verificar configuração embutida

```bash
docker exec devin-mcp-client cat /root/.config/devin/config.json
docker exec devin-mcp-client cat /root/.config/devin/mcp_servers.json
```

## 📚 Documentação Adicional

- [DEVIN_DOCKER_GUIDE.md](DEVIN_DOCKER_GUIDE.md) - Guia completo de integração
- [DISTRIBUTION.md](DISTRIBUTION.md) - Guia de distribuição da imagem
- [AGENTS.md](AGENTS.md) - Regras do projeto (MCP server)

## 🔒 Segurança

- Configuração embutida testada e validada
- Permissões restritivas por padrão
- Sandbox ativo por padrão
- Credenciais isoladas em volume dedicado
- **NUNCA** monte `/var/run/docker.sock` no container do Devin

## 🤝 Contribuindo

Este projeto segue as melhores práticas do tutorial [DataCamp Claude Code Docker](https://www.datacamp.com/tutorial/claude-code-docker) adaptado para o Devin CLI.

## 📄 Licença

Este projeto é uma adaptação para fins educacionais e de desenvolvimento.
