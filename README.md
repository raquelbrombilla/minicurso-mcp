# IA na prática: agentes inteligentes utilizando MCP e Python

Projeto do minicurso. Vamos dar ferramentas para uma IA: um servidor MCP em Python que permite ao GitHub Copilot (ou qualquer aplicação compatível) consultar as notas de um aluno num sistema acadêmico.

No fim, você pergunta para a IA **"Em quais matérias estou em risco e quanto preciso tirar na final?"** e ela descobre sozinha quais ferramentas chamar para responder.

## Como o projeto funciona

```
GitHub Copilot  →  servidor.py  →  api.py  →  academico.db
   (host)         (servidor MCP)   (API)       (banco)
```

| Arquivo | O que é |
| --- | --- |
| `criar_banco.py` | Cria o banco `academico.db` com disciplinas e notas fictícias. |
| `api.py` | A API do "sistema da faculdade", feita com FastAPI. Não sabe nada de IA: é o sistema que já existe. |
| `servidor.py` | **O servidor MCP.** A ponte entre a IA e o sistema: cada função com `@mcp.tool` vira uma ferramenta que a IA pode usar. Por baixo, chama a API. |
| `teste.py` | Testa o servidor pelo Python, sem IA. |
| `agente.py` | Bônus: um agente feito à mão, mostrando o ciclo de tool calling por inteiro. |

As quatro ferramentas que a IA ganha:

- `listar_disciplinas()`: disciplinas, professores e horários.
- `consultar_notas(disciplina)`: as avaliações, com nota e peso.
- `calcular_media(notas, pesos)`: média ponderada.
- `quanto_preciso_na_final(disciplina)`: situação e nota necessária na final.

Regra usada: aprovado direto com média 7 ou mais. Abaixo disso vai para a final e precisa de (média + final) / 2 ≥ 5.

## O que instalar antes

- **Python 3.10 ou superior.** No Windows, marque "Add Python to PATH" na instalação.
- **VS Code**, atualizado.
- **Node.js (versão LTS)**, só para rodar o MCP Inspector.
- Para usar com IA: uma conta no GitHub com o **GitHub Copilot** ativado (o plano gratuito serve).

## Passo a passo

### 1. Baixe o projeto e crie o ambiente virtual

```bash
git clone https://github.com/raquelbrombilla/minicurso-mcp.git
cd minicurso-mcp
python -m venv .venv
```

Ative o ambiente:

```bash
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

### 2. Crie o banco e suba a API

```bash
python criar_banco.py
python api.py
```

Deixe esse terminal aberto: a API precisa ficar rodando. Abra http://127.0.0.1:8000/docs no navegador para ver a documentação e testar os endpoints.

### 3. Teste o servidor MCP sem IA

Num **segundo terminal**, com o ambiente ativado:

```bash
python teste.py
```

Resultado esperado, algo como:

```
Ferramentas: ['listar_disciplinas', 'consultar_notas', 'calcular_media', 'quanto_preciso_na_final']
Cálculo I: {"disciplina":"Cálculo I","media":4.75,"situacao":"final","nota_final_necessaria":5.25}
```

> Não rode `python servidor.py` sozinho esperando ver algo: ele fica parado esperando um cliente MCP. É normal.

### 4. Teste no MCP Inspector

O Inspector é uma tela para testar o servidor sem IA: você faz o papel do modelo.

```bash
npx @modelcontextprotocol/inspector@latest
```

No navegador que abrir, preencha:

| Campo | Valor |
| --- | --- |
| Transport Type | `STDIO` |
| Command | o Python do ambiente virtual, por exemplo `C:\minicurso-mcp\.venv\Scripts\python.exe` |
| Arguments | o caminho do servidor, por exemplo `C:\minicurso-mcp\servidor.py` |

Depois: **Connect → Tools → List Tools**. Escolha `quanto_preciso_na_final`, digite `Cálculo I` e clique em **Run Tool**. Teste também com `Física` para ver a mensagem de erro que ensina a IA a se corrigir.

### 5. Conecte no GitHub Copilot

Abra a pasta do projeto no VS Code. Crie uma pasta `.vscode` e, dentro dela, um arquivo `mcp.json`:

```json
{
  "servers": {
    "assistente-academico": {
      "type": "stdio",
      "command": "C:\\minicurso-mcp\\.venv\\Scripts\\python.exe",
      "args": ["C:\\minicurso-mcp\\servidor.py"]
    }
  }
}
```

São os mesmos três campos do Inspector, só que num arquivo: o tipo de conexão, o programa (o Python do `.venv`) e o que ele roda (o `servidor.py`). O `${workspaceFolder}` é trocado pelo VS Code pela pasta do projeto, então você não precisa escrever o caminho inteiro.

1. Salve o arquivo.
2. Com o arquivo aberto, clique em **Start**, que aparece em cima do nome do servidor.
3. Abra o Copilot Chat, escolha o modo **Agent** e confira no ícone de ferramentas se as quatro tools estão marcadas.

### 6. Pergunte para a IA

Use uma conversa nova para cada pergunta e deixe o terminal da API visível para ver as chamadas chegando:

1. "Quais matérias eu tenho e com quem?"
2. "Como estou em Cálculo I?"
3. "Em quais matérias estou em risco e quanto preciso tirar na final?"
4. "Quanto tirei em Física?"

Na terceira, o esperado é: **Cálculo I** (média 4,75, precisa de 5,25) e **Redes** (média 4,5, precisa de 5,5). Na quarta, a disciplina não existe: a IA lê o erro, chama `listar_disciplinas` e se corrige sozinha.

## Bônus: o agente feito à mão

O `agente.py` faz o papel do Copilot em poucas linhas, para você ver o ciclo de tool calling por dentro: ele manda a pergunta e as ferramentas para o modelo, executa o que o modelo pedir e repete até ele responder com texto.

Precisa de uma chave da API da Anthropic (crie em https://console.anthropic.com; o uso é pago):

```bash
pip install anthropic

# Windows (PowerShell)
$env:ANTHROPIC_API_KEY="sua-chave"

python agente.py "Em quais matérias estou em risco?"
python agente.py --sem-tools "Em quais matérias estou em risco?"
```

As linhas com `->` mostram cada ferramenta que o modelo decidiu chamar. Com `--sem-tools`, ele não recebe nenhuma ferramenta e não tem como responder.

## Usando servidores MCP prontos

Antes de criar um servidor do zero, vale procurar: já existem servidores para GitHub, arquivos, páginas da web, bancos de dados, Notion, Slack e muito mais.

- MCP Registry oficial: https://registry.modelcontextprotocol.io
- Servidores de referência: https://github.com/modelcontextprotocol/servers
- No VS Code: procure `@mcp` na aba de extensões.

Para testar, acrescente um servidor no seu `.vscode/mcp.json`, ao lado do `assistente-academico`. Um servidor roda com as suas permissões, então instale só de fontes confiáveis.

## Desafios

Para quem quiser continuar:

1. **Uma ferramenta nova:** crie `adicionar_nota(disciplina, avaliacao, nota, peso)`. Você vai precisar de um endpoint `POST /notas` na API. Teste primeiro no Inspector.
2. **Um resource:** exponha o horário da semana como `horario://semana` usando `@mcp.resource`.
3. **Um prompt:** crie um prompt `plano_de_estudos` com `@mcp.prompt`, que monte um pedido de cronograma para as matérias em risco.
4. **Seu próprio sistema:** troque o banco e a API por algo que você usa e escreva as ferramentas para ele.
5. **Servidor remoto:** rode o servidor via HTTP com `mcp.run(transport="http")` e conecte pela URL.

## Problemas comuns

| Problema | Solução |
| --- | --- |
| "A API não está rodando" | Abra um terminal e rode `python api.py`. |
| `no such table` | Rode `python criar_banco.py`. |
| O servidor não aparece no Copilot | Confira os caminhos no `mcp.json` (rode `gerar_config.py` de novo), clique em Start e use o modo Agent. |
| `ModuleNotFoundError: fastmcp` | O ambiente virtual não está ativado, ou o `command` do `mcp.json` não aponta para o Python do `.venv`. |
| O servidor quebra sem motivo | Procure um `print()` no `servidor.py`: no stdio ele quebra a comunicação. Use `logging`. |
