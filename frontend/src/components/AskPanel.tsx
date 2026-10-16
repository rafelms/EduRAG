import { useEffect, useState, type FormEvent } from 'react'
import { api, type AskResponse, type DocumentOut } from '../api'
import { errorMessage, formatSeconds } from '../format'
import { SourceList } from './SourceList'

const MAX_CHARS = 2000

interface Props {
  selectedDocuments: DocumentOut[]
  hasReadyDocuments: boolean
}

export function AskPanel({ selectedDocuments, hasReadyDocuments }: Props) {
  const [question, setQuestion] = useState('')
  const [topK, setTopK] = useState(5)
  const [pending, setPending] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const [result, setResult] = useState<{ question: string; response: AskResponse } | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Modelos locais podem levar dezenas de segundos; mostrar o tempo tranquiliza.
  useEffect(() => {
    if (!pending) return
    const started = Date.now()
    const id = setInterval(() => setElapsed(Date.now() - started), 100)
    return () => clearInterval(id)
  }, [pending])

  const trimmed = question.trim()
  const canSubmit = !pending && trimmed.length > 0 && trimmed.length <= MAX_CHARS

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    if (!canSubmit) return
    setElapsed(0)
    setPending(true)
    setError(null)
    try {
      const ids = selectedDocuments.length ? selectedDocuments.map((d) => d.id) : null
      const response = await api.ask(trimmed, ids, topK)
      setResult({ question: trimmed, response })
      setQuestion('')
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setPending(false)
    }
  }

  const scope = selectedDocuments.length
    ? `Buscando em ${selectedDocuments.length} documento(s) selecionado(s)`
    : 'Buscando em todos os documentos'

  return (
    <div className="flex flex-col gap-6">
      <form onSubmit={submit} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <label htmlFor="question" className="sr-only">
          Pergunta
        </label>
        <textarea
          id="question"
          rows={4}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) submit(e)
          }}
          placeholder="Pergunte algo sobre o conteúdo dos documentos…"
          className="w-full resize-y rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 focus:outline-none"
          disabled={pending}
        />
        <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
            <span>{scope}</span>
            <label className="flex items-center gap-1.5" title="Quantos trechos recuperar (1 a 20)">
              Trechos
              <input
                type="number"
                min={1}
                max={20}
                value={topK}
                onChange={(e) => setTopK(Math.min(20, Math.max(1, Number(e.target.value) || 1)))}
                className="w-14 rounded border border-slate-300 px-1.5 py-0.5 text-slate-700"
              />
            </label>
            <span className={trimmed.length > MAX_CHARS ? 'text-red-600' : ''}>
              {trimmed.length}/{MAX_CHARS}
            </span>
          </div>
          <button
            type="submit"
            disabled={!canSubmit}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {pending ? `Gerando… ${formatSeconds(elapsed)}` : 'Perguntar'}
          </button>
        </div>
        {!hasReadyDocuments && (
          <p className="mt-3 text-xs text-amber-700">
            Nenhum documento pronto ainda: envie um PDF e aguarde o processamento.
          </p>
        )}
      </form>

      {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}

      {pending && (
        <div className="animate-pulse rounded-xl border border-slate-200 bg-white p-5">
          <div className="h-3 w-1/3 rounded bg-slate-200" />
          <div className="mt-4 space-y-2">
            <div className="h-3 rounded bg-slate-200" />
            <div className="h-3 w-5/6 rounded bg-slate-200" />
            <div className="h-3 w-2/3 rounded bg-slate-200" />
          </div>
        </div>
      )}

      {result && !pending && (
        <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-sm font-medium text-slate-500">{result.question}</p>
          <p className="mt-3 leading-relaxed whitespace-pre-line text-slate-900">
            {result.response.answer}
          </p>
          <SourceList sources={result.response.sources} />
        </article>
      )}
    </div>
  )
}
