import { Navigate, Route, Routes } from 'react-router-dom'

import { AppLayout } from '@/components/layout/AppLayout'
import { AjustesPage } from '@/pages/AjustesPage'
import { AnadirAccionPage } from '@/pages/AnadirAccionPage'
import { CarteraPage } from '@/pages/CarteraPage'
import { CompanyDetailPage } from '@/pages/CompanyDetailPage'
import { DividendosPage } from '@/pages/DividendosPage'
import { FiabilidadPage } from '@/pages/FiabilidadPage'
import { HoyPage } from '@/pages/HoyPage'
import { MercadoPage } from '@/pages/MercadoPage'
import { ProximamentePage } from '@/pages/ProximamentePage'
import { RankingPage } from '@/pages/RankingPage'

export function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<Navigate to="/mercado" replace />} />
        <Route path="hoy" element={<HoyPage />} />
        <Route path="ranking" element={<RankingPage />} />
        <Route path="mercado" element={<MercadoPage />} />
        <Route path="mercado/:ticker" element={<CompanyDetailPage />} />
        <Route path="cartera" element={<CarteraPage />} />
        <Route path="dividendos" element={<DividendosPage />} />
        <Route path="fiabilidad" element={<FiabilidadPage />} />
        <Route path="anadir-accion" element={<AnadirAccionPage />} />
        <Route path="buscar" element={<ProximamentePage titulo="Buscar" />} />
        <Route path="ajustes" element={<AjustesPage />} />
      </Route>
    </Routes>
  )
}
