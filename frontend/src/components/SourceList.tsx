import type { Source } from '../api'
import { formatScore } from '../format'

export function SourceList({ sources }: { sources: Source[] }) {
  if (sources.length === 0) return null
  return (
    <div className="mt-4">
      <h4 className="mb-2 text-xs font-semibold tracking-wide text-slate-500 uppercase">
        Fontes ({sources.length})
      </h4>
      <ul className="space-y-2">
        {sources.map((s, i) => (
          <li key={`${s.document_id}-${s.page}-${i}`}>
            <details className="group rounded-lg border border-slate-200 bg-slate-50 open:bg-white">
              <summary className="flex cursor-pointer items-center justify-between gap-3 px-3 py-2 text-sm">
                <span className="min-w-0 truncate">
                  <span className="font-medium text-slate-800">{s.filename}</span>
                  <span className="text-slate-500"> · página {s.page}</span>
                </span>
                <span
                  className="shrink-0 rounded bg-indigo-50 px-1.5 py-0.5 text-xs font-medium text-indigo-700"
                  title="Similaridade com a pergunta"
                >
                  {formatScore(s.score)}
                </span>
              </summary>
              <p className="border-t border-slate-200 px-3 py-2 text-sm whitespace-pre-line text-slate-700">
                {s.excerpt}
              </p>
            </details>
          </li>
        ))}
      </ul>
    </div>
  )
}
