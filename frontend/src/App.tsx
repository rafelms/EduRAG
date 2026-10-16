import { useMemo, useState } from 'react'
import { AskPanel } from './components/AskPanel'
import { DocumentsPanel } from './components/DocumentsPanel'
import { HistoryPanel } from './components/HistoryPanel'
import { StatusIndicator } from './components/StatusIndicator'
import { useDocuments } from './useDocuments'

type Tab = 'ask' | 'history'

const TABS: { id: Tab; label: string }[] = [
  { id: 'ask', label: 'Perguntar' },
  { id: 'history', label: 'Histórico' },
]

export default function App() {
  const docs = useDocuments()
  const [tab, setTab] = useState<Tab>('ask')
  const [selected, setSelected] = useState<Set<string>>(new Set())

  const toggle = (id: string) =>
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })

  // Ignora ids de documentos já excluídos ou que deixaram de estar prontos.
  const selectedDocuments = useMemo(
    () => docs.documents.filter((d) => selected.has(d.id) && d.status === 'pronto'),
    [docs.documents, selected],
  )
  const hasReadyDocuments = docs.documents.some((d) => d.status === 'pronto')

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
          <div className="flex items-center gap-2.5">
            <img src="/favicon.svg" alt="" className="h-7 w-7" />
            <div>
              <h1 className="text-lg leading-tight font-semibold">EduRAG</h1>
              <p className="text-xs text-slate-500">Perguntas sobre seus materiais de estudo</p>
            </div>
          </div>
          <StatusIndicator />
        </div>
      </header>

      <main className="mx-auto grid max-w-6xl gap-6 px-4 py-6 lg:grid-cols-[22rem_1fr]">
        <aside>
          <DocumentsPanel {...docs} selected={selected} onToggle={toggle} />
        </aside>

        <section className="min-w-0">
          <nav className="mb-4 flex gap-1 border-b border-slate-200">
            {TABS.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => setTab(t.id)}
                className={`-mb-px border-b-2 px-4 py-2 text-sm font-medium ${
                  tab === t.id
                    ? 'border-indigo-600 text-indigo-700'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                {t.label}
              </button>
            ))}
          </nav>

          {/* AskPanel fica montado para não perder a última resposta ao trocar de aba. */}
          <div hidden={tab !== 'ask'}>
            <AskPanel
              selectedDocuments={selectedDocuments}
              hasReadyDocuments={hasReadyDocuments}
            />
          </div>
          {/* Montado só quando aberto: sempre busca o histórico atualizado. */}
          {tab === 'history' && <HistoryPanel />}
        </section>
      </main>
    </div>
  )
}
