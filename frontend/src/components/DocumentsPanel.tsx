import { useRef, useState, type DragEvent } from 'react'
import { api, type DocumentOut, type DocumentStatus } from '../api'
import { errorMessage, formatDate } from '../format'

interface Props {
  documents: DocumentOut[]
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
  selected: Set<string>
  onToggle: (id: string) => void
}

const STATUS: Record<DocumentStatus, { label: string; className: string }> = {
  processando: { label: 'Processando', className: 'bg-amber-50 text-amber-700 ring-amber-200' },
  pronto: { label: 'Pronto', className: 'bg-emerald-50 text-emerald-700 ring-emerald-200' },
  erro: { label: 'Erro', className: 'bg-red-50 text-red-700 ring-red-200' },
}

export function DocumentsPanel({ documents, loading, error, refresh, selected, onToggle }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [uploading, setUploading] = useState(0)
  const [dragging, setDragging] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)

  const upload = async (files: FileList | File[]) => {
    const pdfs = Array.from(files)
    if (pdfs.length === 0) return
    setActionError(null)
    setUploading((n) => n + pdfs.length)
    const errors: string[] = []
    await Promise.all(
      pdfs.map(async (file) => {
        try {
          await api.uploadDocument(file)
        } catch (err) {
          errors.push(`${file.name}: ${errorMessage(err)}`)
        } finally {
          setUploading((n) => n - 1)
        }
      }),
    )
    if (errors.length) setActionError(errors.join('\n'))
    await refresh()
  }

  const remove = async (doc: DocumentOut) => {
    if (!confirm(`Excluir "${doc.filename}"? Os trechos indexados também serão apagados.`)) return
    setActionError(null)
    try {
      await api.deleteDocument(doc.id)
    } catch (err) {
      setActionError(errorMessage(err))
    }
    await refresh()
  }

  const onDrop = (e: DragEvent) => {
    e.preventDefault()
    setDragging(false)
    upload(e.dataTransfer.files)
  }

  return (
    <section className="flex flex-col gap-4">
      <div className="flex items-baseline justify-between">
        <h2 className="text-base font-semibold text-slate-900">Documentos</h2>
        <span className="text-xs text-slate-500">{documents.length} no total</span>
      </div>

      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={`rounded-xl border-2 border-dashed px-4 py-6 text-center text-sm transition ${
          dragging
            ? 'border-indigo-500 bg-indigo-50 text-indigo-700'
            : 'border-slate-300 text-slate-600 hover:border-indigo-400 hover:bg-slate-50'
        }`}
      >
        {uploading > 0 ? (
          <span>Enviando {uploading} arquivo(s)…</span>
        ) : (
          <>
            <span className="font-medium text-indigo-600">Escolha PDFs</span> ou arraste para cá
          </>
        )}
      </button>
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf,.pdf"
        multiple
        hidden
        onChange={(e) => {
          if (e.target.files) upload(e.target.files)
          e.target.value = ''
        }}
      />

      {(error || actionError) && (
        <p className="rounded-lg bg-red-50 px-3 py-2 text-sm whitespace-pre-line text-red-700">
          {actionError ?? error}
        </p>
      )}

      {loading ? (
        <p className="text-sm text-slate-500">Carregando…</p>
      ) : documents.length === 0 ? (
        <p className="text-sm text-slate-500">Nenhum documento enviado ainda.</p>
      ) : (
        <>
          <p className="text-xs text-slate-500">
            Marque documentos para restringir a busca. Sem seleção, a pergunta usa todos.
          </p>
          <ul className="divide-y divide-slate-100 rounded-xl border border-slate-200 bg-white">
            {documents.map((doc) => {
              const status = STATUS[doc.status]
              const ready = doc.status === 'pronto'
              return (
                <li key={doc.id} className="flex items-start gap-3 px-3 py-2.5">
                  <input
                    type="checkbox"
                    className="mt-1 h-4 w-4 accent-indigo-600 disabled:opacity-40"
                    checked={selected.has(doc.id)}
                    disabled={!ready}
                    onChange={() => onToggle(doc.id)}
                    aria-label={`Usar ${doc.filename} na busca`}
                  />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium text-slate-800" title={doc.filename}>
                      {doc.filename}
                    </p>
                    <p className="mt-0.5 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-slate-500">
                      <span
                        className={`inline-flex items-center gap-1 rounded px-1.5 py-0.5 ring-1 ${status.className}`}
                      >
                        {doc.status === 'processando' && (
                          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-current" />
                        )}
                        {status.label}
                      </span>
                      {doc.pages != null && <span>{doc.pages} pág.</span>}
                      <span>{formatDate(doc.created_at)}</span>
                    </p>
                    {doc.error && <p className="mt-1 text-xs text-red-600">{doc.error}</p>}
                  </div>
                  <button
                    type="button"
                    onClick={() => remove(doc)}
                    className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600"
                    aria-label={`Excluir ${doc.filename}`}
                    title="Excluir"
                  >
                    <svg viewBox="0 0 20 20" fill="currentColor" className="h-4 w-4">
                      <path
                        fillRule="evenodd"
                        d="M8.75 1A2.75 2.75 0 0 0 6 3.75v.443c-.795.077-1.584.176-2.365.298a.75.75 0 1 0 .23 1.482l.149-.022.841 10.518A2.75 2.75 0 0 0 7.596 19h4.807a2.75 2.75 0 0 0 2.742-2.53l.841-10.52.149.023a.75.75 0 0 0 .23-1.482A41.03 41.03 0 0 0 14 4.193V3.75A2.75 2.75 0 0 0 11.25 1h-2.5ZM10 4c.84 0 1.673.025 2.5.075V3.75c0-.69-.56-1.25-1.25-1.25h-2.5c-.69 0-1.25.56-1.25 1.25v.325C8.327 4.025 9.16 4 10 4ZM8.58 7.72a.75.75 0 0 0-1.5.06l.3 7.5a.75.75 0 1 0 1.5-.06l-.3-7.5Zm4.34.06a.75.75 0 1 0-1.5-.06l-.3 7.5a.75.75 0 1 0 1.5.06l.3-7.5Z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </button>
                </li>
              )
            })}
          </ul>
        </>
      )}
    </section>
  )
}
