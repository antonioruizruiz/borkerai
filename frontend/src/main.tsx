import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'

import { App } from '@/App'
import { IndiceProvider } from '@/lib/indiceContext'

import './index.css'

const queryClient = new QueryClient()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <IndiceProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </IndiceProvider>
    </QueryClientProvider>
  </StrictMode>,
)
