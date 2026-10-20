from sqlalchemy import Result, text
from sqlalchemy.orm import Session


def buscar_por_nome(session: Session, nome: str) -> Result:
    sql = "SELECT * FROM documents WHERE filename = '" + nome + "'"
    return session.execute(text(sql))
