"""Testa o servidor MCP direto pelo Python, sem IA e sem Inspector.

Aqui, quem faz o papel do modelo é o próprio código: ele lista as
ferramentas e chama uma delas.

A API precisa estar rodando (python api.py).
Para rodar:  python teste.py
"""
import asyncio
from fastmcp import Client
from servidor import mcp

async def main():
    # Client(mcp) é um cliente MCP conectado ao servidor na memória
    async with Client(mcp) as client:
        tools = await client.list_tools()
        print("Tools:", [t.name for t in tools])

        resultado = await client.call_tool("listar_disciplinas", {})
        print("Disciplinas:", resultado.data)

        resultado = await client.call_tool("quanto_preciso_na_final", {"disciplina": "Cálculo I"})
        print("Cálculo I:", resultado.data)

asyncio.run(main())