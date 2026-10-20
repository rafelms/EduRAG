from sqlalchemy import text


def buscar_por_nome(session, nome):
    sql = "SELECT * FROM documents WHERE filename = '" + nome + "'"
    return session.execute(text(sql))