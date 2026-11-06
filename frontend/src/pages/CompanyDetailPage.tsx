import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'

import { PriceChart } from '@/components/PriceChart'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { getCompanyNews, getCompanyPrices } from '@/lib/api'
import { formatDate } from '@/lib/format'

export function CompanyDetailPage() {
  const { ticker = '' } = useParams()

  const { data, isLoading, isError } = useQuery({
    queryKey: ['prices', ticker],
    queryFn: () => getCompanyPrices(ticker),
    enabled: ticker.length > 0,
  })

  const {
    data: noticias,
    isLoading: cargandoNoticias,
    isError: errorNoticias,
  } = useQuery({
    queryKey: ['news', ticker],
    queryFn: () => getCompanyNews(ticker),
    enabled: ticker.length > 0,
  })

  return (
    <div className="space-y-4">
      <div>
        <Link to="/mercado" className="text-sm text-primary">
          ← Volver a Mercado
        </Link>
        <h1 className="text-2xl font-semibold">{ticker}</h1>
        <p className="text-sm text-muted-foreground">Precio histórico con medias de 50 y 200 sesiones.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Precio</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-muted-foreground">Cargando...</p>}
          {isError && <p className="text-danger">No se ha podido conectar con el backend.</p>}
          {data && data.length === 0 && (
            <p className="text-muted-foreground">
              Todavía no hay histórico descargado para este valor. Lanza{' '}
              <code>python scripts/download_history.py</code> en el backend.
            </p>
          )}
          {data && data.length > 0 && <PriceChart bars={data} />}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Noticias recientes</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {cargandoNoticias && <p className="text-muted-foreground">Cargando...</p>}
          {errorNoticias && <p className="text-danger">No se han podido cargar las noticias.</p>}
          {noticias && noticias.length === 0 && (
            <p className="text-muted-foreground">No se han encontrado noticias recientes.</p>
          )}
          {noticias?.map((item) => (
            <a
              key={item.link}
              href={item.link}
              target="_blank"
              rel="noreferrer"
              className="block rounded-md border border-border p-3 hover:bg-muted"
            >
              <p className="font-medium text-primary">{item.title}</p>
              <p className="text-xs text-muted-foreground">
                {[item.publisher, item.published_at ? formatDate(item.published_at.slice(0, 10)) : null]
                  .filter(Boolean)
                  .join(' · ')}
              </p>
            </a>
          ))}
          <p className="text-xs text-muted-foreground">
            Titulares de prensa vía Google News, no son hechos verificados ni asesoramiento.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
