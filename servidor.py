"""Servidor MCP do assistente acadêmico.

É a ponte entre a IA e o sistema da faculdade: cada função com @mcp.tool
vira uma ferramenta (tool) que o modelo pode pedir para usar. Por baixo, as
ferramentas chamam a API (api.py).

A API precisa estar rodando (python api.py).
Quem inicia este servidor é o cliente MCP (Inspector, Copilot...),
não você. Rodar "python servidor.py" sozinho parece travar: é normal,
ele está esperando um cliente.

Atenção: não use print() aqui. No stdio, a saída padrão é o canal do
protocolo, e um print quebra a comunicação.
"""

import httpx
from fastmcp import FastMCP

API = "http://127.0.0.1:8000"
mcp = FastMCP("Assistente Acadêmico")

# Funções auxiliares ---------------------------------------------------
# Lógica comum, reaproveitada pelas tools. Elas não têm @mcp.tool,
# então a IA não as vê: são só código Python.
def buscar_notas(disciplina: str) -> list[dict]:
    try:
        resposta = httpx.get(f"{API}/notas", params={"disciplina": disciplina})
    except httpx.ConnectError:
        raise RuntimeError("A API não está rodando. Inicie com: python api.py")
    if resposta.status_code == 404:
        # Mensagem escrita para a IA ler e se corrigir sozinha
        raise ValueError(
            f"Disciplina '{disciplina}' não encontrada. "
            "Use listar_disciplinas para ver os nomes válidos."
        )
    resposta.raise_for_status()
    return resposta.json()

def media_ponderada(notas: list[float], pesos: list[float]) -> float:
    if not notas or len(notas) != len(pesos):
        raise ValueError("notas e pesos devem ter o mesmo tamanho (maior que zero)")
    return round(sum(n * p for n, p in zip(notas, pesos)) / sum(pesos), 2)

# Tools -----------------------------------------------------------------
# O nome da função, os tipos dos parâmetros e a docstring viram a
# descrição que o modelo lê para decidir quando usar cada ferramenta.
# É por isso que falamos que "precisamos documentar o MCP para IA".

@mcp.tool
def listar_disciplinas() -> list[dict]:
    """Lista as disciplinas em que o aluno está matriculado,
    com professor e horário."""
    try:
        resposta = httpx.get(f"{API}/disciplinas")
    except httpx.ConnectError:
        raise RuntimeError("A API não está rodando. Inicie com: python api.py")
    resposta.raise_for_status()
    return resposta.json()


@mcp.tool
def consultar_notas(disciplina: str) -> list[dict]:
    """Retorna as notas e pesos de cada avaliação de uma disciplina.
    Use o nome exato retornado por listar_disciplinas."""
    return buscar_notas(disciplina)


@mcp.tool
def calcular_media(notas: list[float], pesos: list[float]) -> float:
    """Calcula a média ponderada. As listas devem ter o mesmo tamanho."""
    return media_ponderada(notas, pesos)


@mcp.tool
def quanto_preciso_na_final(disciplina: str) -> dict:
    """Calcula a situação do aluno numa disciplina e quanto ele
    precisa tirar na prova final. Aprovado direto com média >= 7;
    na final, precisa de (média + final) / 2 >= 5.
    Use o nome exato retornado por listar_disciplinas."""
    avaliacoes = buscar_notas(disciplina)
    media = media_ponderada(
        [a["nota"] for a in avaliacoes], [a["peso"] for a in avaliacoes])
    if media >= 7:
        return {"disciplina": disciplina, "media": media,
                "situacao": "aprovado", "nota_final_necessaria": 0}
    precisa = round(10 - media, 2)
    return {"disciplina": disciplina, "media": media,
            "situacao": "final" if precisa <= 10 else "reprovado",
            "nota_final_necessaria": precisa}

if __name__ == "__main__":
    mcp.run(transport="stdio")