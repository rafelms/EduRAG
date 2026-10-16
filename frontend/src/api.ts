// Cliente da API EduRAG. Os tipos espelham app/api/schemas.py.

const BASE_URL: string = import.meta.env.VITE_API_BASE_URL || '/api'

export type DocumentStatus = 'processando' | 'pronto' | 'erro'

export interface DocumentOut {
  id: string
  filename: string
  status: DocumentStatus
  pages: number | null
  error: string | null
  created_at: string
}

export interface DocumentCreated {
  id: string
  status: DocumentStatus
}

export interface Source {
  document_id: string
  filename: string
  page: number
  excerpt: string
  score: number
}

export interface AskResponse {
  question_id: string
  answer: string
  sources: Source[]
}

export interface QuestionOut {
  id: string
  question: string
  answer: string
  sources: Source[]
  model: string
  latency_ms: number
  created_at: string
}

export interface QuestionsPage {
  items: QuestionOut[]
  total: number
  limit: number
  offset: number
}

export type Readiness = { status: 'ready' } | { status: 'unavailable'; failed: string[] }

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

// FastAPI devolve `detail` como texto (HTTPException) ou lista (erro de validação).
function detailMessage(body: unknown, status: number): string {
  const detail = (body as { detail?: unknown } | null)?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail
      .map((d: { msg?: string }) => (d.msg ?? '').replace(/^Value error, /, ''))
      .filter(Boolean)
      .join('; ')
  }
  return `Erro inesperado (HTTP ${status}).`
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${BASE_URL}${path}`, init)
  } catch {
    throw new ApiError(0, 'Não foi possível conectar à API.')
  }
  if (response.status === 204) return undefined as T
  const body: unknown = await response.json().catch(() => null)
  if (!response.ok) throw new ApiError(response.status, detailMessage(body, response.status))
  return body as T
}

export const api = {
  // /ready responde 503 com o mesmo formato de corpo, então não passa por request().
  ready: async (): Promise<Readiness> => {
    const response = await fetch(`${BASE_URL}/ready`)
    if (response.status !== 200 && response.status !== 503) {
      throw new ApiError(response.status, 'API indisponível.')
    }
    return (await response.json()) as Readiness
  },

  listDocuments: () => request<DocumentOut[]>('/documents'),

  uploadDocument: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return request<DocumentCreated>('/documents', { method: 'POST', body: form })
  },

  deleteDocument: (id: string) => request<void>(`/documents/${id}`, { method: 'DELETE' }),

  ask: (question: string, documentIds: string[] | null, topK: number) =>
    request<AskResponse>('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, document_ids: documentIds, top_k: topK }),
    }),

  listQuestions: (limit: number, offset: number) =>
    request<QuestionsPage>(`/questions?limit=${limit}&offset=${offset}`),
}
