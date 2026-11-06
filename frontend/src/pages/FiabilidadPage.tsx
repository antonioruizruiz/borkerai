import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Bar, BarChart, CartesianGrid, ReferenceLine, Tooltip, XAxis, YAxis } from 'recharts'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { getFiabilidad, type OperacionBacktest, type ResumenRegla } from '@/lib/api'
import { formatDate, formatPct, formatPrecio } from '@/lib/format'
import { useIndiceSeleccionado } from '@/lib/indiceContext'
import { cn } from '@/lib/utils'

const OPERACIONES_POR_PAGINA = 25

function Metrica({ etiqueta, valor }: { etiqueta: string; valor: string }) {
  return (
    <div>
      <p className="text-xs text-muted-foreground">{etiqueta}</p>
      <p className="text-xl font-semibold">{valor}</p>
    </div>
  )
}

function TarjetaRegla({ nombre, resumen }: { nombre: string; resumen: ResumenRegla }) {
  return (
    <div className="rounded-lg border border-border p-4">
      <p className="font-medium">{nombre}</p>
      <div className="mt-2 grid grid-cols-2 gap-3 text-sm">
        <div>
          <p className="text-xs text-muted-foreground">Operaciones</p>
          <p className="font-medium">{resumen.n_operaciones}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Tasa de acierto</p>
          <p className="font-medium">{resumen.tasa_acierto_pct != null ? `${resumen.tasa_acierto_pct}%` : '—'}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Retorno medio</p>
          <p className="font-medium">{resumen.retorno_medio_pct != null ? formatPct(resumen.retorno_medio_pct) : '—'}</p>
        </div>
        <div>
          <p className="text-xs text-muted-foreground">Beneficio/riesgo neto medio</p>
          <p className="font-medium">
            {resumen.beneficio_riesgo_neto_medio != null ? `${resumen.beneficio_riesgo_neto_medio.toFixed(2)}x` : '—'}
          </p>
        </div>
      </div>
    </div>
  )
}

const COLOR_MOTIVO: Record<OperacionBacktest['motivo_salida'], string> = {
  objetivo: 'text-success',
  stop: 'text-danger',
  tiempo: 'text-muted-foreground',
}

export function FiabilidadPage() {
  const { indiceParaApi } = useIndiceSeleccionado()
  const { data, isLoading, isError } = useQuery({
    queryKey: ['fiabilidad', indiceParaApi],
    queryFn: () => getFiabilidad(indiceParaApi),
  })
  const [pagina, setPagina] = useState(0)

  const datosSeguimiento = data
    ? Object.entries(data.seguimiento_medio).map(([clave, valor]) => ({
        horizonte: clave.replace('d', 'D+').replace('_pct', ''),
        valor,
      }))
    : []

  const operacionesOrdenadas = data ? [...data.operaciones].sort((a, b) => (a.fecha_entrada < b.fecha_entrada ? 1 : -1)) : []
  const totalPaginas = Math.ceil(operacionesOrdenadas.length / OPERACIONES_POR_PAGINA)
  const operacionesPagina = operacionesOrdenadas.slice(
    pagina * OPERACIONES_POR_PAGINA,
    (pagina + 1) * OPERACIONES_POR_PAGINA,
  )

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Fiabilidad</h1>
        <p className="text-sm text-muted-foreground">
          Backtest de las reglas de la página Hoy sobre los 10 años de histórico ya descargados: qué habría pasado
          si se hubieran seguido todas las señales pasadas, con comisiones y deslizamiento ya descontados. Son
          resultados pasados: no garantizan nada sobre el futuro.
        </p>
      </div>

      {isLoading && <p className="text-muted-foreground">Calculando el backtest (puede tardar unos segundos)...</p>}
      {isError && <p className="text-danger">No se ha podido conectar con el backend.</p>}

      {data && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>Resumen global ({data.resumen_global.n_operaciones} operaciones)</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              <Metrica
                etiqueta="Tasa de acierto"
                valor={data.resumen_global.tasa_acierto_pct != null ? `${data.resumen_global.tasa_acierto_pct}%` : '—'}
              />
              <Metrica
                etiqueta="Retorno medio por operación"
                valor={data.resumen_global.retorno_medio_pct != null ? formatPct(data.resumen_global.retorno_medio_pct) : '—'}
              />
              <Metrica
                etiqueta="Beneficio/riesgo neto medio"
                valor={
                  data.resumen_global.beneficio_riesgo_neto_medio != null
                    ? `${data.resumen_global.beneficio_riesgo_neto_medio.toFixed(2)}x`
                    : '—'
                }
              />
              <Metrica
                etiqueta="Índice de referencia en el mismo periodo"
                valor={data.comparacion_indice ? formatPct(data.comparacion_indice.retorno_total_pct) : '—'}
              />
            </CardContent>
          </Card>

          {!data.comparacion_indice && data.comparacion_indice_nota && (
            <Card>
              <CardContent className="py-4 text-sm text-muted-foreground">{data.comparacion_indice_nota}</CardContent>
            </Card>
          )}

          {data.comparacion_indice && (
            <Card>
              <CardHeader>
                <CardTitle>Comparación con el índice</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <p className="text-muted-foreground">
                  Del {formatDate(data.comparacion_indice.fecha_inicio)} al {formatDate(data.comparacion_indice.fecha_fin)}
                  , el índice habría dado un <strong>{formatPct(data.comparacion_indice.retorno_total_pct)}</strong> total
                  (
                  {data.comparacion_indice.retorno_anualizado_pct != null
                    ? formatPct(data.comparacion_indice.retorno_anualizado_pct)
                    : '—'}{' '}
                  anualizado) simplemente comprando y manteniendo, sin hacer nada. El sistema, operación a operación,
                  ha dado de media un <strong>{formatPct(data.resumen_global.retorno_medio_pct ?? 0)}</strong> por
                  operación. Son medidas distintas (una es "todo el periodo de una vez", la otra es "por operación
                  individual"): sirven para hacerse una idea, no para una comparación exacta.
                </p>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardHeader>
              <CardTitle>Desglose por regla</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-3 sm:grid-cols-2">
              {Object.entries(data.por_regla).map(([nombre, resumen]) => (
                <TarjetaRegla key={nombre} nombre={nombre} resumen={resumen} />
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Seguimiento medio tras cada señal</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="mb-2 text-sm text-muted-foreground">
                Variación media del precio, en %, a los 1/5/10/20 días de sesión de activarse una señal (sin tener
                en cuenta el stop ni el objetivo).
              </p>
              <BarChart width={560} height={200} data={datosSeguimiento} margin={{ left: 8, right: 8 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="horizonte" />
                <YAxis />
                <Tooltip formatter={(valor) => `${Number(valor).toFixed(2)}%`} />
                <ReferenceLine y={0} stroke="#64748b" />
                <Bar dataKey="valor" fill="#4338ca" radius={[4, 4, 0, 0]} />
              </BarChart>
            </CardContent>
          </Card>

          <Card className="overflow-hidden">
            <CardHeader>
              <CardTitle>
                Historial de operaciones simuladas ({operacionesOrdenadas.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border text-left text-muted-foreground">
                    <th className="px-5 py-3 font-medium">Empresa</th>
                    <th className="px-5 py-3 font-medium">Regla</th>
                    <th className="px-5 py-3 font-medium">Entrada</th>
                    <th className="px-5 py-3 font-medium">Salida</th>
                    <th className="px-5 py-3 font-medium">Motivo</th>
                    <th className="px-5 py-3 text-right font-medium">Retorno</th>
                    <th className="px-5 py-3 text-right font-medium">B/R neto</th>
                  </tr>
                </thead>
                <tbody>
                  {operacionesPagina.map((op, i) => (
                    <tr key={`${op.ticker}-${op.fecha_entrada}-${i}`} className="border-b border-border last:border-0">
                      <td className="px-5 py-3">
                        <span className="font-medium">{op.ticker}</span>
                        <span className="ml-1 text-muted-foreground">{op.name}</span>
                      </td>
                      <td className="px-5 py-3 text-muted-foreground">{op.regla}</td>
                      <td className="px-5 py-3">
                        {formatDate(op.fecha_entrada)} ({formatPrecio(op.entrada, op.moneda)})
                      </td>
                      <td className="px-5 py-3">
                        {formatDate(op.fecha_salida)} ({formatPrecio(op.precio_salida, op.moneda)})
                      </td>
                      <td className={cn('px-5 py-3', COLOR_MOTIVO[op.motivo_salida])}>{op.motivo_salida}</td>
                      <td className={cn('px-5 py-3 text-right font-medium', op.retorno_pct >= 0 ? 'text-success' : 'text-danger')}>
                        {formatPct(op.retorno_pct)}
                      </td>
                      <td className="px-5 py-3 text-right">
                        {op.beneficio_riesgo_neto != null ? `${op.beneficio_riesgo_neto.toFixed(2)}x` : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {totalPaginas > 1 && (
                <div className="flex items-center justify-between px-5 py-3 text-sm text-muted-foreground">
                  <button
                    className="disabled:opacity-40"
                    disabled={pagina === 0}
                    onClick={() => setPagina((p) => Math.max(0, p - 1))}
                  >
                    ← Anteriores
                  </button>
                  <span>
                    Página {pagina + 1} de {totalPaginas}
                  </span>
                  <button
                    className="disabled:opacity-40"
                    disabled={pagina >= totalPaginas - 1}
                    onClick={() => setPagina((p) => Math.min(totalPaginas - 1, p + 1))}
                  >
                    Siguientes →
                  </button>
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
