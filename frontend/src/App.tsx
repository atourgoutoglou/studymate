import { useState } from 'react'
import type { FormEvent } from 'react'

type Source = {
  file: string
  page: number
  text: string
}

type Message = {
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    const text = question.trim()
    if (!text || loading) return

    setMessages((previous) => [...previous, { role: 'user', content: text }])
    setQuestion('')
    setLoading(true)

    try {
      const response = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text }),
      })
      if (!response.ok) {
        throw new Error(`Request failed (${response.status})`)
      }
      const data: { answer: string; sources: Source[] } = await response.json()
      setMessages((previous) => [
        ...previous,
        { role: 'assistant', content: data.answer, sources: data.sources },
      ])
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Something went wrong'
      setMessages((previous) => [...previous, { role: 'assistant', content: `⚠️ ${message}` }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen flex-col bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <h1 className="text-xl font-semibold">📚 StudyMate</h1>
        <p className="text-sm text-slate-500">
          Ask questions about your PDFs. Every answer cites the file and page.
        </p>
      </header>

      <main className="flex-1 overflow-y-auto px-6 py-6">
        <div className="mx-auto flex max-w-3xl flex-col gap-4">
          {messages.length === 0 && (
            <p className="mt-20 text-center text-slate-400">Ask your first question to get started.</p>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={
                message.role === 'user'
                  ? 'max-w-[80%] self-end rounded-2xl bg-indigo-600 px-4 py-2 text-white'
                  : 'max-w-[80%] self-start rounded-2xl bg-white px-4 py-3 shadow-sm'
              }
            >
              <p className="whitespace-pre-wrap">{message.content}</p>

              {message.sources && message.sources.length > 0 && (
                <details className="mt-2 text-sm text-slate-600">
                  <summary className="cursor-pointer font-medium">
                    Sources ({message.sources.length})
                  </summary>
                  <ul className="mt-2 flex flex-col gap-2">
                    {message.sources.map((source, i) => (
                      <li key={i} className="rounded-lg bg-slate-100 p-2">
                        <span className="font-semibold">
                          {source.file}, page {source.page}
                        </span>
                        <p className="mt-1 line-clamp-3">{source.text}</p>
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          ))}

          {loading && <p className="self-start text-slate-400">Thinking...</p>}
        </div>
      </main>

      <form onSubmit={handleSubmit} className="border-t border-slate-200 bg-white px-6 py-4">
        <div className="mx-auto flex max-w-3xl gap-2">
          <input
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask a question about your documents..."
            className="flex-1 rounded-xl border border-slate-300 px-4 py-2 outline-none focus:border-indigo-500"
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="rounded-xl bg-indigo-600 px-5 py-2 font-medium text-white disabled:opacity-50"
          >
            Ask
          </button>
        </div>
      </form>
    </div>
  )
}

export default App