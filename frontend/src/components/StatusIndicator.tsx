import { useEffect, useState } from 'react'
import { api } from '../api'

type State = { tone: 'ok' | 'warn' | 'down' | 'unknown'; label: string }

const COMPONENTS: Record<string, string> = { database: 'banco', ollama: 'Ollama' }

const DOT = {
  ok: 'bg-emerald-500',
  warn: 'bg-amber-500',
  down: 'bg-red-500',
  unknown: 'bg-slate-400',
}

export function StatusIndicator() {
  const [state, setState] = useState<State>({ tone: 'unknown', label: 'Verificando…' })

  useEffect(() => {
    let active = true
    const check = async () => {
      try {
        const r = await api.ready()
        if (!active) return
        if (r.status === 'ready') setState({ tone: 'ok', label: 'Serviços prontos' })
        else {
          const names = r.failed.map((f) => COMPONENTS[f] ?? f).join(' e ')
          setState({ tone: 'warn', label: `Indisponível: ${names}` })
        }
      } catch {
        if (active) setState({ tone: 'down', label: 'API fora do ar' })
      }
    }
    check()
    const id = setInterval(check, 30_000)
    return () => {
      active = false
      clearInterval(id)
    }
  }, [])

  return (
    <span className="flex items-center gap-2 text-sm text-slate-600">
      <span className={`h-2.5 w-2.5 rounded-full ${DOT[state.tone]}`} aria-hidden />
      {state.label}
    </span>
  )
}
