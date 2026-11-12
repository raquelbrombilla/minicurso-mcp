"""API do "sistema da faculdade".

Uma API comum, feita com FastAPI, que lê o banco academico.db.
Ela não sabe nada de IA nem de MCP: é o sistema que já existe.

Para rodar:   python api.py
Documentação: http://127.0.0.1:8000/docs
"""

import sqlite3
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException

BANCO = Path(__file__).parent / "academico.db"

app = FastAPI(title="Sistema Acadêmico")


def conectar():
    con = sqlite3.connect(BANCO)
    con.row_factory = sqlite3.Row
    return con


@app.get("/disciplinas")
def listar_disciplinas():
    """Lista as disciplinas com professor e horário."""
    with conectar() as con:
        linhas = con.execute(
            "SELECT nome, professor, horario FROM disciplinas"
        ).fetchall()
    return [dict(l) for l in linhas]


@app.get("/notas")
def consultar_notas(disciplina: str):
    """Retorna as avaliações (nota e peso) de uma disciplina."""
    with conectar() as con:
        linhas = con.execute(
            """SELECT n.avaliacao, n.nota, n.peso
               FROM notas n JOIN disciplinas d ON d.id = n.disciplina_id
               WHERE d.nome = ?""",
            (disciplina,),  # consulta com parâmetro: nunca monte SQL com f-string
        ).fetchall()
    if not linhas:
        raise HTTPException(status_code=404, detail="Disciplina não encontrada")
    return [dict(l) for l in linhas]


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
