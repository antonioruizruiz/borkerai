# CLAUDE.md — Contexto del proyecto "Broker IBEX 35"

## Qué es
Aplicación web para **estudiar el IBEX 35**: tendencias, histórico de cotizaciones, ranking de empresas,
panel de recomendaciones, cartera personal y **simulaciones (backtest)** de haber seguido las recomendaciones.
Es una herramienta de estudio personal, **no asesoramiento financiero**.

Inspiración visual y funcional: capturas `Captura de pantalla 2026-10-30 *.png` en la raíz (app "Trading AI").

## Sobre el usuario
Antonio no tiene experiencia programando. Por tanto:
- Explica en español y en lenguaje sencillo qué vas a hacer **antes** de hacerlo y qué has hecho al terminar.
- Trabaja en pasos pequeños y verificables. Al final de cada paso, di **cómo probarlo** (comando exacto y qué debería ver).
- **Todo se ejecuta en Linux (de momento WSL/Ubuntu local; más adelante VPS Ubuntu por SSH)**: da siempre comandos de bash para Ubuntu, nunca de PowerShell/Windows.
- Si algo necesita `sudo` o abrir puertos, avisa antes y explica por qué.
- No introduzcas librerías o servicios nuevos sin justificarlo y avisar.
- Sugiere hacer `git commit` cuando algo quede funcionando.

## Principio de diseño clave
**La IA no decide sola.** Flujo de análisis diario:
1. Datos de mercado (precios, volumen, dividendos) →
2. Filtro cuantitativo en Python (factores 0–100: momentum, tendencia, calidad, valoración, estabilidad, fuerza del sector) →
3. Generación de plan (orden límite, stop, objetivo, plazo, beneficio/riesgo neto de costes) →
4. Revisión con la API de Claude (noticias, hechos relevantes CNMV, riesgos) que puede **matizar o frenar**, nunca inventar compras →
5. Seguimiento de cada recomendación (D+1, D+5, D+10, D+20) para medir **Fiabilidad**.

## Stack
- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2, Pydantic v2, pandas, pandas-ta, APScheduler, SDK `anthropic`.
- **BD**: SQLite en desarrollo (`backend/data/broker.db`), PostgreSQL en producción.
- **Datos**: `yfinance` (tickers `.MC`) para el prototipo, detrás de una interfaz `MarketDataProvider` para poder cambiar a un proveedor de pago (EODHD / Twelve Data / FMP) sin tocar el resto.
- **Frontend**: React + Vite + TypeScript + Tailwind CSS + shadcn/ui; gráficas con TradingView Lightweight Charts (precio) y Recharts (barras/factores). React Query para llamadas a la API.
- **Despliegue**: VPS Ubuntu, Docker Compose (backend, frontend estático, postgres) + Caddy (HTTPS automático).

## Estructura
```
broker/
├── CLAUDE.md            ← este archivo
├── ROADMAP.md           ← fases y estado
├── GUIA_CLAUDE_CODE.md  ← cómo trabajar con Claude Code + prompts por fase
├── backend/
│   ├── app/
│   │   ├── main.py          (FastAPI, rutas bajo /api)
│   │   ├── core/config.py   (configuración desde .env)
│   │   ├── data/ibex35.py   (universo de valores)
│   │   ├── api/             (routers)
│   │   ├── models/          (SQLAlchemy)
│   │   ├── services/        (datos, scoring, backtest, IA)
│   │   └── jobs/            (tarea diaria)
│   └── tests/
├── frontend/            (se crea en la Fase 2 con Vite)
└── deploy/              (docker-compose, Caddyfile — Fase 8)
```

## Convenciones
- Código y nombres en inglés; textos de la interfaz, comentarios clave y explicaciones en **español**.
- Moneda EUR, formato español (1.234,56 €), fechas dd/mm/aaaa, zona horaria Europe/Madrid.
- Los secretos (API keys) van en `backend/.env`, **nunca** en git. Plantilla en `backend/.env.example`.
- Cada endpoint nuevo con al menos un test en `backend/tests/` (pytest).
- Costes de operación configurables (comisión, mínimo, deslizamiento) y descontados siempre en simulaciones.
- Llamadas a la API de Claude: registrar tokens y coste estimado en BD para mostrarlo en Ajustes.

## Entorno de trabajo
- **Fase actual (desarrollo): WSL (Ubuntu) dentro del propio PC Windows de Antonio.** El proyecto vive en
  `/mnt/d/GIT/proyectos_propios/broker` (su disco D: de Windows, montado en WSL). No hay servidor remoto todavía.
- Como WSL2 reenvía automáticamente `localhost` al Windows anfitrión, Antonio abre `http://localhost:8000` y
  `http://localhost:5173` directamente en su navegador de Windows, **sin necesidad de túnel SSH**.
- El código se sincroniza igualmente con un repositorio git privado en GitHub (buena práctica y copia de seguridad),
  aunque de momento no haya un VPS al que desplegar.
- **VPS Ubuntu remoto por SSH**: se incorporará solo en la **Fase 8 (despliegue)**. Cuando llegue ese momento, Antonio
  se conectará por SSH desde Windows (idealmente VS Code + Remote-SSH) y los servidores de producción escucharán solo
  en `localhost`, vistos mediante túnel SSH; no se abrirán los puertos 8000/5173 al exterior.

## Comandos (bash, Ubuntu/WSL)
```bash
# Backend (desde ~/broker/backend o, en WSL, desde la carpeta del proyecto en /mnt/d/...)
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                 # solo la primera vez
uvicorn app.main:app --reload        # http://localhost:8000/docs
pytest

# Frontend (desde ~/broker/frontend, a partir de la Fase 2)
npm install
npm run dev                          # http://localhost:5173
```
