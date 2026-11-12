"""Cria o banco academico.db com dados fictícios.

É o "sistema da faculdade" do projeto: a API (api.py) lê deste banco.
Rode uma vez antes de tudo:  python criar_banco.py
"""

import sqlite3

con = sqlite3.connect("academico.db")
con.executescript("""
DROP TABLE IF EXISTS notas;
DROP TABLE IF EXISTS disciplinas;
CREATE TABLE disciplinas (
    id INTEGER PRIMARY KEY,
    nome TEXT UNIQUE NOT NULL,
    professor TEXT,
    horario TEXT
);
CREATE TABLE notas (
    disciplina_id INTEGER REFERENCES disciplinas(id),
    avaliacao TEXT,
    nota REAL,
    peso REAL
);
""")
disciplinas = [
    (1, "Cálculo I", "Prof. Ana", "Seg 19h"),
    (2, "Algoritmos", "Prof. Bruno", "Ter 19h"),
    (3, "Banco de Dados", "Prof. Carla", "Qua 19h"),
    (4, "Redes", "Prof. Diego", "Qui 19h"),
]
notas = [
    (1, "P1", 4.5, 1), (1, "P2", 5.0, 1),
    (2, "P1", 8.0, 1), (2, "P2", 9.0, 1),
    (3, "P1", 6.0, 2), (3, "Trabalho", 9.0, 1),
    (4, "P1", 3.0, 1), (4, "P2", 6.0, 1),
]
con.executemany("INSERT INTO disciplinas VALUES (?, ?, ?, ?)", disciplinas)
con.executemany("INSERT INTO notas VALUES (?, ?, ?, ?)", notas)
con.commit()
con.close()
print("Banco criado: academico.db")