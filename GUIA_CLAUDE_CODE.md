# Guía rápida: trabajar con Claude Code en este proyecto (WSL local → más adelante VPS Ubuntu)

De momento desarrollamos en **WSL (Ubuntu) dentro de tu propio PC Windows**, en la carpeta
`/mnt/d/GIT/proyectos_propios/broker` (tu disco D:). El VPS Ubuntu remoto por SSH se deja para la
**Fase 8 (despliegue)**: cuando llegue ese momento añadiremos de nuevo los pasos de Remote-SSH y túnel.

## Fase 0 paso a paso

### 1. Herramientas básicas (ya hecho)
Ya tienes instalados en este WSL: `git` 2.25.1, `node` v22.13.1 (vía `nvm`) y `npm` 11.6.3. No hace falta tocar nada aquí.

### 2. Python 3.12
Tu WSL es Ubuntu 20.04 (focal), que solo trae Python 3.8 de serie. Hace falta añadir el repositorio
`deadsnakes` para instalar 3.12. Esto pide `sudo` (te pedirá tu contraseña de Linux):
```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev

# Comprobar
python3.12 --version    # debería decir Python 3.12.x
```

### 3. Claude Code
Ya está instalado y funcionando (es lo que estás usando ahora mismo).

### 4. Recrear el entorno virtual del backend con 3.12
El `.venv` que ya existe se creó con Python 3.8, así que hay que rehacerlo:
```bash
cd /mnt/d/GIT/proyectos_propios/broker/backend
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # solo si no existe ya
pytest                    # deberían salir 2 passed
uvicorn app.main:app --reload --port 8000
```
Abre en tu navegador de Windows **http://localhost:8000/docs** — funciona directamente, sin túnel SSH,
porque WSL2 reenvía automáticamente los puertos `localhost` a Windows.

### 5. Subir el proyecto a GitHub (repositorio privado)
Esto es buena práctica y copia de seguridad, aunque todavía no haya un VPS al que desplegar:
```bash
cd /mnt/d/GIT/proyectos_propios/broker
git init
git add .
git commit -m "Esqueleto inicial"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/broker.git   # crea antes el repo PRIVADO en GitHub
git push -u origin main
```
A partir de aquí sigues trabajando **en esta misma carpeta de WSL**; el push a GitHub es solo copia de seguridad.

## Arrancar Claude Code
```bash
cd ~/broker
claude
```
Lee automáticamente `CLAUDE.md`, así que ya conoce el proyecto.

## Atajos y comandos útiles
| Qué | Cómo |
|---|---|
| Modo plan (propone antes de tocar nada) | `Shift+Tab` hasta ver "plan mode" |
| Señalar un archivo | `@backend/app/main.py` |
| Interrumpir | `Esc` |
| Empezar conversación limpia (al cambiar de tarea) | `/clear` |
| Ver ayuda | `/help` |
| Pasar una captura | Arrástrala al explorador de VS Code (se sube al VPS) y escribe su ruta, p. ej. `@capturas/error.png` |

## Rutina por cada tarea
1. `/clear`
2. Pide la tarea concreta en **modo plan**.
3. Lee el plan; si algo no te convence, dilo.
4. Acepta y deja que lo haga.
5. Pruébalo tú siguiendo las instrucciones que te dé.
6. Si falla, pega el error **completo**.
7. Cuando funcione: `git add . && git commit -m "Fase X: ..." && git push`

## Prompts de arranque por fase (cópialos tal cual)

**Fase 1**
> Lee CLAUDE.md y ROADMAP.md. Vamos con la Fase 1. Primero crea los modelos de base de datos y el servicio de datos con yfinance. Explícame el plan antes de escribir código y dime al final cómo probarlo.

**Fase 2**
> Fase 2 del ROADMAP. Crea el frontend con Vite + React + TypeScript + Tailwind + shadcn/ui en la carpeta frontend. Quiero la barra superior como en las capturas de la raíz. Empieza solo por la estructura y la página Mercado.

**Fase 3**
> Fase 3. Calcula los indicadores y factores 0–100 para los 35 valores. Antes de programar, explícame en lenguaje sencillo qué mide cada factor.

**Para errores**
> Al ejecutar `<comando>` me sale este error: <pegar error completo>. Explícame qué pasa y arréglalo.

**Para entender**
> Explícame qué hace @backend/app/services/scoring.py como si no supiera programar.
