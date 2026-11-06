"""Universo inicial del IBEX 35 (tickers de Yahoo Finance con sufijo .MC, EUR).

OJO: la composición del índice cambia en las revisiones trimestrales.
Revisar contra la web de BME antes de usar y, en la Fase 1, pasar esta lista a la BD.
"""

IBEX35 = [
    {"ticker": "ACS.MC", "name": "ACS", "sector": "Construcción", "moneda": "EUR"},
    {"ticker": "ACX.MC", "name": "Acerinox", "sector": "Materiales", "moneda": "EUR"},
    {"ticker": "AENA.MC", "name": "Aena", "sector": "Transporte", "moneda": "EUR"},
    {"ticker": "AMS.MC", "name": "Amadeus", "sector": "Tecnología", "moneda": "EUR"},
    {"ticker": "ANA.MC", "name": "Acciona", "sector": "Construcción", "moneda": "EUR"},
    {"ticker": "ANE.MC", "name": "Acciona Energía", "sector": "Energía", "moneda": "EUR"},
    {"ticker": "BBVA.MC", "name": "BBVA", "sector": "Banca", "moneda": "EUR"},
    {"ticker": "BKT.MC", "name": "Bankinter", "sector": "Banca", "moneda": "EUR"},
    {"ticker": "CABK.MC", "name": "CaixaBank", "sector": "Banca", "moneda": "EUR"},
    {"ticker": "CLNX.MC", "name": "Cellnex", "sector": "Telecomunicaciones", "moneda": "EUR"},
    {"ticker": "COL.MC", "name": "Inmobiliaria Colonial", "sector": "Inmobiliario", "moneda": "EUR"},
    {"ticker": "ELE.MC", "name": "Endesa", "sector": "Utilities", "moneda": "EUR"},
    {"ticker": "ENG.MC", "name": "Enagás", "sector": "Utilities", "moneda": "EUR"},
    {"ticker": "FDR.MC", "name": "Fluidra", "sector": "Industria", "moneda": "EUR"},
    {"ticker": "FER.MC", "name": "Ferrovial", "sector": "Construcción", "moneda": "EUR"},
    {"ticker": "GRF.MC", "name": "Grifols", "sector": "Salud", "moneda": "EUR"},
    {"ticker": "IAG.MC", "name": "IAG", "sector": "Transporte", "moneda": "EUR"},
    {"ticker": "IBE.MC", "name": "Iberdrola", "sector": "Utilities", "moneda": "EUR"},
    {"ticker": "IDR.MC", "name": "Indra", "sector": "Tecnología", "moneda": "EUR"},
    {"ticker": "ITX.MC", "name": "Inditex", "sector": "Consumo", "moneda": "EUR"},
    {"ticker": "LOG.MC", "name": "Logista", "sector": "Distribución", "moneda": "EUR"},
    {"ticker": "MAP.MC", "name": "Mapfre", "sector": "Seguros", "moneda": "EUR"},
    {"ticker": "MRL.MC", "name": "Merlin Properties", "sector": "Inmobiliario", "moneda": "EUR"},
    {"ticker": "MTS.MC", "name": "ArcelorMittal", "sector": "Materiales", "moneda": "EUR"},
    {"ticker": "NTGY.MC", "name": "Naturgy", "sector": "Utilities", "moneda": "EUR"},
    {"ticker": "PUIG.MC", "name": "Puig", "sector": "Consumo", "moneda": "EUR"},
    {"ticker": "RED.MC", "name": "Redeia", "sector": "Utilities", "moneda": "EUR"},
    {"ticker": "REP.MC", "name": "Repsol", "sector": "Energía", "moneda": "EUR"},
    {"ticker": "ROVI.MC", "name": "Laboratorios Rovi", "sector": "Salud", "moneda": "EUR"},
    {"ticker": "SAB.MC", "name": "Banco Sabadell", "sector": "Banca", "moneda": "EUR"},
    {"ticker": "SAN.MC", "name": "Banco Santander", "sector": "Banca", "moneda": "EUR"},
    {"ticker": "SCYR.MC", "name": "Sacyr", "sector": "Construcción", "moneda": "EUR"},
    {"ticker": "SLR.MC", "name": "Solaria", "sector": "Energía", "moneda": "EUR"},
    {"ticker": "TEF.MC", "name": "Telefónica", "sector": "Telecomunicaciones", "moneda": "EUR"},
    {"ticker": "UNI.MC", "name": "Unicaja", "sector": "Banca", "moneda": "EUR"},
]
