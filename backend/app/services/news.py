"""Noticias relacionadas con una empresa, vía el feed RSS público de Google News.

No añade ninguna librería nueva (usa `httpx`, ya presente en requirements.txt) ni
requiere API key. Pensado como ayuda de contexto ("¿qué pudo mover la cotización?"),
no como fuente exhaustiva ni verificada: son titulares de prensa, no hechos contrastados.
"""
from __future__ import annotations

from datetime import datetime
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

import httpx
from pydantic import BaseModel

GOOGLE_NEWS_RSS_URL = "https://news.google.com/rss/search"


class NewsItem(BaseModel):
    title: str
    publisher: str | None
    link: str
    published_at: datetime | None


def get_company_news(query: str, max_items: int = 3) -> list[NewsItem]:
    """Últimos titulares (máx. `max_items`) relacionados con `query` (p. ej. nombre de empresa)."""
    params = {
        "q": f"{query} acciones bolsa",
        "hl": "es-ES",
        "gl": "ES",
        "ceid": "ES:es",
    }
    try:
        respuesta = httpx.get(GOOGLE_NEWS_RSS_URL, params=params, timeout=10, follow_redirects=True)
        respuesta.raise_for_status()
    except httpx.HTTPError:
        return []

    try:
        raiz = ElementTree.fromstring(respuesta.text)
    except ElementTree.ParseError:
        return []

    noticias: list[NewsItem] = []
    for item in raiz.findall("./channel/item")[:max_items]:
        titulo_completo = (item.findtext("title") or "").strip()
        enlace = (item.findtext("link") or "").strip()
        fecha_texto = item.findtext("pubDate")

        # Google News da el título como "Titular - Medio"; separamos el medio si aparece.
        titulo, _, medio = titulo_completo.rpartition(" - ")
        if not titulo:
            titulo, medio = titulo_completo, None

        publicado = None
        if fecha_texto:
            try:
                publicado = parsedate_to_datetime(fecha_texto)
            except (TypeError, ValueError):
                publicado = None

        noticias.append(
            NewsItem(title=titulo, publisher=medio or None, link=enlace, published_at=publicado)
        )

    return noticias
