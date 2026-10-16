import { useCallback, useEffect, useState } from 'react'
import { api, type DocumentOut } from './api'
import { errorMessage } from './format'

const POLL_MS = 3000

// Lista de documentos; consulta de novo enquanto algum ainda está sendo processado.
export function useDocuments() {
  const [documents, setDocuments] = useState<DocumentOut[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    try {
      setDocuments(await api.listDocuments())
      setError(null)
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    // refresh() só altera o estado depois do await; não há render em cascata.
    // oxlint-disable-next-line react/set-state-in-effect
    refresh()
  }, [refresh])

  const processing = documents.some((d) => d.status === 'processando')
  useEffect(() => {
    if (!processing) return
    const id = setInterval(refresh, POLL_MS)
    return () => clearInterval(id)
  }, [processing, refresh])

  return { documents, loading, error, refresh }
}
