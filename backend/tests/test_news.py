import httpx
from fastapi.testclient import TestClient

from app.main import app
import app.services.news as news_service

client = TestClient(app)

RSS_DE_EJEMPLO = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel>
<item>
  <title>BBVA sube en bolsa tras resultados - Cinco Días</title>
  <link>https://news.google.com/rss/articles/abc</link>
  <pubDate>Mon, 02 Nov 2026 09:00:00 GMT</pubDate>
</item>
<item>
  <title>Análisis: qué esperar del sector bancario</title>
  <link>https://news.google.com/rss/articles/def</link>
  <pubDate>Sun, 01 Nov 2026 18:30:00 GMT</pubDate>
</item>
<item>
  <title>BBVA anuncia nuevo plan estratégico - Expansión</title>
  <link>https://news.google.com/rss/articles/ghi</link>
  <pubDate>Sat, 31 Oct 2026 12:00:00 GMT</pubDate>
</item>
<item>
  <title>Noticia de más, no debería aparecer - Reuters</title>
  <link>https://news.google.com/rss/articles/jkl</link>
  <pubDate>Fri, 30 Oct 2026 12:00:00 GMT</pubDate>
</item>
</channel></rss>"""


def _respuesta_ok(texto: str) -> httpx.Response:
    return httpx.Response(200, text=texto, request=httpx.Request("GET", "https://news.google.com/rss/search"))


def test_get_company_news_parsea_titulo_medio_y_fecha(monkeypatch):
    def fake_get(*args, **kwargs):
        return _respuesta_ok(RSS_DE_EJEMPLO)

    monkeypatch.setattr(news_service.httpx, "get", fake_get)

    noticias = news_service.get_company_news("BBVA", max_items=3)

    assert len(noticias) == 3
    assert noticias[0].title == "BBVA sube en bolsa tras resultados"
    assert noticias[0].publisher == "Cinco Días"
    assert noticias[0].published_at is not None
    # Sin " - Medio" al final, el título se queda entero y no hay medio.
    assert noticias[1].publisher is None


def test_get_company_news_si_falla_la_red_devuelve_lista_vacia(monkeypatch):
    def fake_get(*args, **kwargs):
        raise httpx.ConnectError("sin red")

    monkeypatch.setattr(news_service.httpx, "get", fake_get)

    assert news_service.get_company_news("BBVA") == []


def test_endpoint_noticias_empresa_desconocida_404(db_session):
    r = client.get("/api/companies/NOEXISTE.MC/news")
    assert r.status_code == 404


def test_endpoint_noticias_devuelve_lo_que_da_el_servicio(db_session, monkeypatch):
    def fake_get(*args, **kwargs):
        return _respuesta_ok(RSS_DE_EJEMPLO)

    monkeypatch.setattr(news_service.httpx, "get", fake_get)

    r = client.get("/api/companies/BBVA.MC/news")
    assert r.status_code == 200
    noticias = r.json()
    assert len(noticias) == 3
    assert noticias[0]["title"] == "BBVA sube en bolsa tras resultados"
