import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { borrarEmpresaSuelta, crearEmpresaSuelta, getCompanies, type CompanyCreateInput } from '@/lib/api'
import { formatPrecio } from '@/lib/format'
import { cn } from '@/lib/utils'

const MONEDAS = ['EUR', 'USD', 'CHF', 'GBP', 'DKK']

const FORMULARIO_INICIAL: CompanyCreateInput = { ticker: '', name: '', sector: '', moneda: 'EUR' }

export function AnadirAccionPage() {
  const queryClient = useQueryClient()
  const { data: sueltas, isLoading, isError } = useQuery({
    queryKey: ['companies', 'NINGUNO'],
    queryFn: () => getCompanies('NINGUNO'),
  })
  const [formulario, setFormulario] = useState<CompanyCreateInput>(FORMULARIO_INICIAL)

  const invalidarListados = () => {
    queryClient.invalidateQueries({ queryKey: ['companies'] })
    queryClient.invalidateQueries({ queryKey: ['indices'] })
  }

  const crear = useMutation({
    mutationFn: crearEmpresaSuelta,
    onSuccess: () => {
      invalidarListados()
      setFormulario(FORMULARIO_INICIAL)
    },
  })

  const borrar = useMutation({
    mutationFn: borrarEmpresaSuelta,
    onSuccess: invalidarListados,
  })

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Añadir acción</h1>
        <p className="text-sm text-muted-foreground">
          Empresas que no pertenecen a ningún índice seguido (IBEX 35, Dow Jones, Nasdaq-100), para hacerles
          seguimiento igualmente. Al añadir una, se descarga de inmediato su histórico de precios de los últimos 10
          años desde Yahoo Finance: el ticker debe ser el de Yahoo Finance (p. ej. <code>MC.PA</code> para LVMH en
          París, <code>NESN.SW</code> para Nestlé en Zúrich).
        </p>
      </div>

      <Card className="max-w-xl">
        <CardHeader>
          <CardTitle>Nueva acción</CardTitle>
        </CardHeader>
        <CardContent>
          <form
            className="grid grid-cols-2 gap-3"
            onSubmit={(e) => {
              e.preventDefault()
              if (!formulario.ticker || !formulario.name || !formulario.sector) return
              crear.mutate({
                ...formulario,
                ticker: formulario.ticker.trim().toUpperCase(),
                name: formulario.name.trim(),
                sector: formulario.sector.trim(),
              })
            }}
          >
            <label className="text-sm">
              Ticker (Yahoo Finance)
              <input
                type="text"
                placeholder="Ej. MC.PA"
                className="mt-1 w-full rounded-md border border-border bg-transparent px-2 py-1.5 text-sm"
                value={formulario.ticker}
                onChange={(e) => setFormulario({ ...formulario, ticker: e.target.value })}
                required
              />
            </label>

            <label className="text-sm">
              Moneda
              <select
                className="mt-1 w-full rounded-md border border-border bg-transparent px-2 py-1.5 text-sm"
                value={formulario.moneda}
                onChange={(e) => setFormulario({ ...formulario, moneda: e.target.value })}
              >
                {MONEDAS.map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </label>

            <label className="col-span-2 text-sm">
              Nombre
              <input
                type="text"
                placeholder="Ej. LVMH"
                className="mt-1 w-full rounded-md border border-border bg-transparent px-2 py-1.5 text-sm"
                value={formulario.name}
                onChange={(e) => setFormulario({ ...formulario, name: e.target.value })}
                required
              />
            </label>

            <label className="col-span-2 text-sm">
              Sector
              <input
                type="text"
                placeholder="Ej. Lujo"
                className="mt-1 w-full rounded-md border border-border bg-transparent px-2 py-1.5 text-sm"
                value={formulario.sector}
                onChange={(e) => setFormulario({ ...formulario, sector: e.target.value })}
                required
              />
            </label>

            <div className="col-span-2">
              <Button type="submit" disabled={crear.isPending}>
                {crear.isPending ? 'Añadiendo (descargando histórico)...' : 'Añadir'}
              </Button>
              {crear.isError && (
                <p className="mt-2 text-sm text-danger">{(crear.error as Error).message}</p>
              )}
            </div>
          </form>
        </CardContent>
      </Card>

      <Card className="overflow-hidden">
        <CardHeader>
          <CardTitle>Acciones sueltas ({sueltas?.length ?? 0})</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          {isLoading && <p className="p-5 text-muted-foreground">Cargando...</p>}
          {isError && <p className="p-5 text-danger">No se ha podido conectar con el backend.</p>}
          {sueltas && sueltas.length === 0 && (
            <p className="p-5 text-muted-foreground">Todavía no has añadido ninguna acción suelta.</p>
          )}
          {sueltas && sueltas.length > 0 && (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-muted-foreground">
                  <th className="px-5 py-3 font-medium">Ticker</th>
                  <th className="px-5 py-3 font-medium">Empresa</th>
                  <th className="px-5 py-3 font-medium">Sector</th>
                  <th className="px-5 py-3 text-right font-medium">Precio</th>
                  <th className="px-5 py-3" />
                </tr>
              </thead>
              <tbody>
                {sueltas.map((c) => (
                  <tr key={c.ticker} className={cn('border-b border-border last:border-0')}>
                    <td className="px-5 py-3">
                      <Link to={`/mercado/${c.ticker}`} className="font-medium text-primary">
                        {c.ticker}
                      </Link>
                    </td>
                    <td className="px-5 py-3">{c.name}</td>
                    <td className="px-5 py-3 text-muted-foreground">{c.sector}</td>
                    <td className="px-5 py-3 text-right">
                      {c.last_price != null ? formatPrecio(c.last_price, c.moneda) : '—'}
                    </td>
                    <td className="px-5 py-3 text-right">
                      <Button variant="ghost" size="sm" onClick={() => borrar.mutate(c.ticker)} disabled={borrar.isPending}>
                        Borrar
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
