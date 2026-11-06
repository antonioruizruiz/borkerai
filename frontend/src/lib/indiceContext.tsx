import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'

export const TODOS = 'TODOS'

const CLAVE_LOCALSTORAGE = 'broker.indiceSeleccionado'

interface IndiceContextValue {
  /** "TODOS" (sin filtro), "IBEX35" / "DOWJONES" / "NASDAQ100", o "NINGUNO" (sueltas). */
  indice: string
  setIndice: (indice: string) => void
  /** `undefined` cuando es "TODOS", listo para pasar directamente a las funciones de `api.ts`. */
  indiceParaApi: string | undefined
}

const IndiceContext = createContext<IndiceContextValue | null>(null)

export function IndiceProvider({ children }: { children: ReactNode }) {
  const [indice, setIndice] = useState<string>(() => {
    try {
      return localStorage.getItem(CLAVE_LOCALSTORAGE) ?? TODOS
    } catch {
      return TODOS
    }
  })

  useEffect(() => {
    try {
      localStorage.setItem(CLAVE_LOCALSTORAGE, indice)
    } catch {
      // almacenamiento no disponible (p. ej. navegación privada): no pasa nada, simplemente no persiste
    }
  }, [indice])

  return (
    <IndiceContext.Provider value={{ indice, setIndice, indiceParaApi: indice === TODOS ? undefined : indice }}>
      {children}
    </IndiceContext.Provider>
  )
}

export function useIndiceSeleccionado(): IndiceContextValue {
  const ctx = useContext(IndiceContext)
  if (!ctx) {
    throw new Error('useIndiceSeleccionado debe usarse dentro de <IndiceProvider>')
  }
  return ctx
}
