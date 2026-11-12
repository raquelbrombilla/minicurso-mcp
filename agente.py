"""Um agente feito à mão: o ciclo de tool calling por inteiro.

Faz o mesmo papel do Copilot (host), só que em poucas linhas:
  1. conecta no servidor MCP e descobre as ferramentas;
  2. manda a conversa + a lista de ferramentas para o modelo;
  3. se o modelo pedir uma ferramenta, executa no servidor MCP;
  4. devolve o resultado para o modelo e repete;
  5. para quando o modelo responder com texto.

Precisa de uma chave da API da Anthropic na variável ANTHROPIC_API_KEY
(crie em https://console.anthropic.com) e de:  pip install anthropic

A API precisa estar rodando (python api.py).

Uso:
  python agente.py "Em quais matérias estou em risco?"
  python agente.py --sem-tools "Em quais matérias estou em risco?"
"""

import asyncio
import sys
from pathlib import Path
from anthropic import Anthropic
from fastmcp import Client
from dotenv import load_dotenv

MODELO = "claude-haiku-5-5"  # modelo barato e rápido para a demo
load_dotenv(Path(__file__).parent / ".env") 
llm = Anthropic()  # lê a chave da variável ANTHROPIC_API_KEY

async def agente(pergunta: str, usar_tools: bool = True):
    # Client("servidor.py") inicia o servidor MCP como subprocesso (stdio)
    async with Client("servidor.py") as mcp:
        # 1. Descobrir as tools do servidor e converter para o formato da API
        tools = [
            {"name": t.name,
             "description": t.description or "",
             "input_schema": t.inputSchema}
            for t in await mcp.list_tools()
        ] if usar_tools else []

        print(f"Tools disponíveis: {[t['name'] for t in tools] or 'nenhuma'}\n")
        mensagens = [{"role": "user", "content": pergunta}]

        while True:
            # 2. Mandar a conversa + a lista de tools ao modelo
            resp = llm.messages.create(
                model=MODELO, max_tokens=1024,
                tools=tools, messages=mensagens)
            mensagens.append({"role": "assistant", "content": resp.content})

            # 3. Se o modelo não pediu nenhuma tool, ele terminou
            if resp.stop_reason != "tool_use":
                print("\nResposta:")
                print("".join(b.text for b in resp.content if b.type == "text"))
                return

            # 4. Executar no servidor MCP cada tool que o modelo pediu
            resultados = []
            for bloco in resp.content:
                if bloco.type != "tool_use":
                    continue
                print(f"-> {bloco.name}({bloco.input})")
                try:
                    r = await mcp.call_tool(bloco.name, bloco.input)
                    texto = "\n".join(c.text for c in r.content if c.type == "text")
                    erro = False
                except Exception as e:
                    texto, erro = f"Erro: {e}", True
                resultados.append({"type": "tool_result",
                                   "tool_use_id": bloco.id,
                                   "content": texto,
                                   "is_error": erro})

            # 5. Devolver os resultados ao modelo e repetir o loop
            mensagens.append({"role": "user", "content": resultados})

if __name__ == "__main__":
    args = sys.argv[1:]
    usar_tools = "--sem-tools" not in args
    args = [a for a in args if a != "--sem-tools"]
    pergunta = " ".join(args) or (
        "Em quais matérias estou em risco e quanto preciso tirar na final?"
    )
    asyncio.run(agente(pergunta, usar_tools))

