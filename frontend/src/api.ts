import type { DocumentInfo, Source } from './types'

// Turns a failed response into a readable message.
async function errorMessage(response: Response): Promise<string> {
  try {
    const data = await response.json()
    if (typeof data.detail === 'string') return data.detail
  } catch {
    // The body was not JSON, so we fall back to the status code.
  }
  return `Request failed (${response.status})`
}

export async function askQuestion(
  question: string,
): Promise<{ answer: string; sources: Source[] }> {
  const response = await fetch('/api/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })
  if (!response.ok) throw new Error(await errorMessage(response))
  return response.json()
}

export async function listDocuments(): Promise<DocumentInfo[]> {
  const response = await fetch('/api/documents')
  if (!response.ok) throw new Error(await errorMessage(response))
  return response.json()
}

export async function uploadDocument(file: File): Promise<DocumentInfo[]> {
  const form = new FormData()
  form.append('file', file)
  const response = await fetch('/api/documents', { method: 'POST', body: form })
  if (!response.ok) throw new Error(await errorMessage(response))
  return response.json()
}