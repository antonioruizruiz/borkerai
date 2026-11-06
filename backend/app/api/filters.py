"""Filtro de índice compartido por los routers que listan `Company`."""
from sqlalchemy.orm import Query

from app.models.company import Company


def filtrar_por_indice(query: Query, indice: str | None) -> Query:
    """Sin `indice`, devuelve la query sin tocar (universo completo). Con
    `indice="NINGUNO"`, filtra las acciones sueltas (sin índice). Con cualquier
    otro valor, filtra por ese índice exacto ("IBEX35", "DOWJONES", "NASDAQ100")."""
    if indice is None:
        return query
    if indice.upper() == "NINGUNO":
        return query.filter(Company.indice.is_(None))
    return query.filter(Company.indice == indice.upper())
