import { useQuery } from '@tanstack/react-query'
import { NavLink } from 'react-router-dom'

import { getIndices } from '@/lib/api'
import { TODOS, useIndiceSeleccionado } from '@/lib/indiceContext'
import { cn } from '@/lib/utils'

const TABS = [
  { to: '/hoy', label: 'Hoy' },
  { to: '/ranking', label: 'Ranking' },
  { to: '/mercado', label: 'Mercado' },
  { to: '/cartera', label: 'Cartera' },
  { to: '/dividendos', label: 'Dividendos' },
  { to: '/fiabilidad', label: 'Fiabilidad' },
  { to: '/anadir-accion', label: 'Añadir acción' },
  { to: '/buscar', label: 'Buscar' },
  { to: '/ajustes', label: 'Ajustes' },
]

function SelectorIndice() {
  const { data: indices } = useQuery({ queryKey: ['indices'], queryFn: getIndices })
  const { indice, setIndice } = useIndiceSeleccionado()

  return (
    <select
      className="rounded-md border border-border bg-transparent px-2 py-1.5 text-sm"
      value={indice}
      onChange={(e) => setIndice(e.target.value)}
      title="Filtrar las páginas de Mercado, Ranking, Fiabilidad y Dividendos por índice"
    >
      <option value={TODOS}>Todos los índices</option>
      {indices?.map((info) => (
        <option key={info.indice ?? 'NINGUNO'} value={info.indice ?? 'NINGUNO'}>
          {info.nombre} ({info.n_empresas})
        </option>
      ))}
    </select>
  )
}

export function TopNav() {
  return (
    <header className="border-b border-border bg-card">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-6 px-4">
        <span className="font-semibold text-foreground">Broker Multi-índice</span>

        <nav className="flex flex-1 items-center gap-1 overflow-x-auto">
          {TABS.map((tab) => (
            <NavLink
              key={tab.to}
              to={tab.to}
              className={({ isActive }) =>
                cn(
                  'whitespace-nowrap rounded-md px-3 py-1.5 text-sm font-medium text-muted-foreground transition-colors hover:text-foreground',
                  isActive && 'bg-muted text-foreground',
                )
              }
            >
              {tab.label}
            </NavLink>
          ))}
        </nav>

        <SelectorIndice />
      </div>
    </header>
  )
}
