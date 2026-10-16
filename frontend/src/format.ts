const dateTime = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' })

export const formatDate = (iso: string) => dateTime.format(new Date(iso))

export const formatScore = (score: number) => `${Math.round(score * 100)}%`

export const formatSeconds = (ms: number) => `${(ms / 1000).toFixed(1).replace('.', ',')} s`

export const errorMessage = (err: unknown) =>
  err instanceof Error ? err.message : 'Erro inesperado.'
