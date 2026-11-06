"""Acciones sueltas sin índice de referencia (indice=None en Company).

Elegidas para cubrir sectores/geografías que no están en IBEX35/DowJones/Nasdaq-100
(lujo europeo, consumo defensivo suizo/danés, software alemán), evitando solapar con
esos tres universos. Es solo la semilla inicial: desde la página "Añadir acción" del
frontend se pueden sumar más empresas sueltas sin tocar este fichero (se guardan
directamente en la base de datos).

Casos a destacar:
- Porsche: existen DOS cotizadas distintas. Se elige Porsche AG (P911.DE, el fabricante
  de coches que salió a bolsa en 2022) en vez de Porsche SE (PAH3.DE, la holding familiar
  cuyo valor depende sobre todo de su participación en Volkswagen) porque representa el
  negocio real de la marca, que es lo que se espera al elegir "Porsche".
- Ferrari cotiza a la vez en Milán (RACE.MI, EUR) y en Nueva York (RACE, USD, mismo
  ticker). Se usa la cotización de Milán porque es la plaza de origen/referencia de la
  empresa y mantiene la coherencia de "moneda original" con el resto del grupo europeo.
- Novo Nordisk cotiza en Copenhague (NOVO-B.CO, DKK) y como ADR en Nueva York (NVO, USD).
  Se usa Copenhague por ser la cotización original danesa.
- Diageo cotiza en Londres (DGE.L); Yahoo Finance da ese precio en PENIQUES (GBp), no en
  libras. No hace falta ningún cambio de código con una sola empresa en GBP, pero queda
  anotado por si se añaden más empresas de Londres en el futuro.
"""

SUELTAS = [
    {"ticker": "MC.PA", "name": "LVMH", "sector": "Lujo", "moneda": "EUR"},
    {"ticker": "P911.DE", "name": "Porsche AG", "sector": "Automoción", "moneda": "EUR"},
    {"ticker": "RACE.MI", "name": "Ferrari", "sector": "Automoción", "moneda": "EUR"},
    {"ticker": "RMS.PA", "name": "Hermès", "sector": "Lujo", "moneda": "EUR"},
    {"ticker": "OR.PA", "name": "L'Oréal", "sector": "Consumo", "moneda": "EUR"},
    {"ticker": "NESN.SW", "name": "Nestlé", "sector": "Consumo", "moneda": "CHF"},
    {"ticker": "NOVO-B.CO", "name": "Novo Nordisk", "sector": "Salud", "moneda": "DKK"},
    {"ticker": "SAP.DE", "name": "SAP", "sector": "Tecnología", "moneda": "EUR"},
    {"ticker": "CFR.SW", "name": "Richemont", "sector": "Lujo", "moneda": "CHF"},
    {"ticker": "DGE.L", "name": "Diageo", "sector": "Consumo", "moneda": "GBP"},
]
