import { useEffect, useState } from 'react'
import { api, type QuestionsPage } from '../api'
import { errorMessage, formatDate, formatSeconds } from '../format'
import { SourceList } from './SourceList'

const PAGE_SIZE = 10

export function HistoryPanel() {
  const [offset, setOffset] = useState(0)
  const [page, setPage] = useState<QuestionsPage | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    api
      .listQuestions(PAGE_SIZE, offset)
      .then((p) => {
        if (active) setPage(p)
      })
      .catch((err) => {
        if (active) setError(errorMessage(err))
      })
    return () => {
      active = false
    }
  }, [offset])

  if (error) return <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>
  if (!page) return <p className="text-sm text-slate-500">Carregando…</p>
  if (page.total === 0) return <p className="text-sm text-slate-500">Nenhuma pergunta feita ainda.</p>

  const last = Math.min(offset + PAGE_SIZE, page.total)

  return (
    <div className="flex flex-col gap-3">
      <ul className="space-y-3">
        {page.items.map((q) => (
          <li key={q.id}>
            <details className="rounded-xl border border-slate-200 bg-white shadow-sm">
              <summary className="cursor-pointer px-4 py-3">
                <span className="text-sm font-medium text-slate-900">{q.question}</span>
                <span className="mt-1 block text-xs text-slate-500">
                  {formatDate(q.created_at)} · {q.model} · {formatSeconds(q.latency_ms)}
                </span>
              </summary>
              <div className="border-t border-slate-100 px-4 py-3">
                <p className="leading-relaxed whitespace-pre-line text-slate-800">{q.answer}</p>
                <SourceList sources={q.sources} />
              </div>
            </details>
          </li>
        ))}
      </ul>

      <div className="flex items-center justify-between text-sm text-slate-600">
        <span>
          {offset + 1}–{last} de {page.total}
        </span>
        <div className="flex gap-2">
          <button
            type="button"
            disabled={offset === 0}
            onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
            className="rounded-lg border border-slate-300 px-3 py-1 hover:bg-slate-50 disabled:opacity-40"
          >
            Anterior
          </button>
          <button
            type="button"
            disabled={last >= page.total}
            onClick={() => setOffset(offset + PAGE_SIZE)}
            className="rounded-lg border border-slate-300 px-3 py-1 hover:bg-slate-50 disabled:opacity-40"
          >
            Próxima
          </button>
        </div>
      </div>
    </div>
  )
}
