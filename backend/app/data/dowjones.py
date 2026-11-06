"""Universo del Dow Jones Industrial Average (30 valores, tickers de Yahoo Finance).

Todos cotizan en NYSE o Nasdaq, en USD, por eso casi ninguno lleva sufijo de bolsa
(a diferencia de IBEX35, que usa `.MC`). OJO: el Dow Jones y el Nasdaq-100 comparten
varios valores (p. ej. MSFT, NVDA, AMZN, CSCO, HON, AMGN); la regla para no duplicarlos
en `Company` vive en `universo.py` (gana Nasdaq-100), no aquí: esta lista refleja la
composición real del índice tal cual, sin deduplicar.

Revisar contra S&P Dow Jones Indices antes de usar (recomposición poco frecuente,
pero ocurre: p. ej. NVDA sustituyó a Intel y AMZN a Walgreens en 2024).
"""

DOWJONES = [
    {"ticker": "AAPL", "name": "Apple", "sector": "Tecnología", "moneda": "USD"},
    {"ticker": "MSFT", "name": "Microsoft", "sector": "Tecnología", "moneda": "USD"},
    {"ticker": "UNH", "name": "UnitedHealth Group", "sector": "Salud", "moneda": "USD"},
    {"ticker": "GS", "name": "Goldman Sachs", "sector": "Banca", "moneda": "USD"},
    {"ticker": "HD", "name": "Home Depot", "sector": "Consumo", "moneda": "USD"},
    {"ticker": "CAT", "name": "Caterpillar", "sector": "Industria", "moneda": "USD"},
    {"ticker": "MCD", "name": "McDonald's", "sector": "Consumo", "moneda": "USD"},
    {"ticker": "V", "name": "Visa", "sector": "Finanzas", "moneda": "USD"},
    {"ticker": "AMGN", "name": "Amgen", "sector": "Salud", "moneda": "USD"},
    {"ticker": "CRM", "name": "Salesforce", "sector": "Tecnología", "moneda": "USD"},
    {"ticker": "BA", "name": "Boeing", "sector": "Industria", "moneda": "USD"},
    {"ticker": "HON", "name": "Honeywell", "sector": "Industria", "moneda": "USD"},
    {"ticker": "AXP", "name": "American Express", "sector": "Finanzas", "moneda": "USD"},
    {"ticker": "JPM", "name": "JPMorgan Chase", "sector": "Banca", "moneda": "USD"},
    {"ticker": "TRV", "name": "Travelers", "sector": "Seguros", "moneda": "USD"},
    {"ticker": "IBM", "name": "IBM", "sector": "Tecnología", "moneda": "USD"},
    {"ticker": "PG", "name": "Procter & Gamble", "sector": "Consumo", "moneda": "USD"},
    {"ticker": "CVX", "name": "Chevron", "sector": "Energía", "moneda": "USD"},
    {"ticker": "MRK", "name": "Merck", "sector": "Salud", "moneda": "USD"},
    {"ticker": "WMT", "name": "Walmart", "sector": "Consumo", "moneda": "USD"},
    {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Salud", "moneda": "USD"},
    {"ticker": "NKE", "name": "Nike", "sector": "Consumo", "moneda": "USD"},
    {"ticker": "DIS", "name": "Walt Disney", "sector": "Consumo", "moneda": "USD"},
    {"ticker": "KO", "name": "Coca-Cola", "sector": "Consumo", "moneda": "USD"},
    {"ticker": "CSCO", "name": "Cisco Systems", "sector": "Tecnología", "moneda": "USD"},
    {"ticker": "MMM", "name": "3M", "sector": "Industria", "moneda": "USD"},
    {"ticker": "VZ", "name": "Verizon", "sector": "Telecomunicaciones", "moneda": "USD"},
    {"ticker": "NVDA", "name": "NVIDIA", "sector": "Tecnología", "moneda": "USD"},
    {"ticker": "SHW", "name": "Sherwin-Williams", "sector": "Materiales", "moneda": "USD"},
    {"ticker": "AMZN", "name": "Amazon", "sector": "Consumo", "moneda": "USD"},
]
