import { useEffect, useRef, useState } from 'react'
import type { FormEvent, KeyboardEvent } from 'react'
import type { DocumentInfo, Message } from './types'
import { askQuestion, listDocuments, uploadDocument } from './api'
import Sidebar from './components/Sidebar'
import Answer from './components/Answer'
import Logo, { Mark } from './components/Logo'
import { BookIcon, LightbulbIcon, ListIcon, ScaleIcon, SendIcon } from './components/Icons'
import ThemeToggle from './components/ThemeToggle'
import { useTheme } from './useTheme'

const SUGGESTIONS = [
  { icon: BookIcon, text: 'What is retrieval-augmented generation?' },
  { icon: LightbulbIcon, text: 'How are large language models trained?' },
  { icon: ScaleIcon, text: 'What are the limits of RAG?' },
  { icon: ListIcon, text: 'Summarize the main results of the RAG paper' },
]

export default function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [documents, setDocuments] = useState<DocumentInfo[]>([])
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const { theme, toggleTheme } = useTheme()

  // Load the library once, when the page opens.
  useEffect(() => {
    listDocuments()
      .then(setDocuments)
      .catch(() => setUploadError('Could not reach the backend. Start uvicorn and refresh.'))
  }, [])

  // Scroll to the newest message.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function ask(text: string) {
    const trimmed = text.trim()
    if (!trimmed || loading) return

    setMessages((prev) => [...prev, { role: 'user', content: trimmed }])
    setQuestion('')
    setLoading(true)

    try {
      const data = await askQuestion(trimmed)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.answer, sources: data.sources },
      ])
    } catch (err) {
      const reason = err instanceof Error ? err.message : 'Something went wrong'
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `${reason}. Check that the backend is running and try again.` },
      ])
    } finally {
      setLoading(false)
    }
  }

  async function handleUpload(file: File) {
    setUploading(true)
    setUploadError(null)
    try {
      setDocuments(await uploadDocument(file))
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    ask(question)
  }

  // Enter sends, Shift+Enter makes a new line.
  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      ask(question)
    }
  }

  const empty = messages.length === 0

  return (
    <div className="flex h-screen">
      <Sidebar
        documents={documents}
        uploading={uploading}
        error={uploadError}
        onUpload={handleUpload}
        onNewChat={() => setMessages([])}
        theme={theme}
        onToggleTheme={toggleTheme}
      />

      <div className="flex min-w-0 flex-1 flex-col">
        {/* Header for phones, where the sidebar is hidden */}
        <header className="flex items-center justify-between border-b border-line bg-surface px-5 py-3 md:hidden">
          <Logo />
          <span className="rounded-full bg-brand-soft px-3 py-1 text-xs font-semibold text-brand">
            {documents.length} PDFs
          </span>
        </header>

        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-3xl px-5 py-10">
            {empty ? (
              <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
                <Mark size="h-14 w-14" />
                <h1 className="mt-6 text-3xl font-extrabold tracking-tight md:text-4xl">
                  Ask your study material anything
                </h1>
                <p className="mt-3 max-w-md text-muted">
                  StudyMate reads your PDFs and answers with the exact pages it used,
                  so you can trust every line.
                </p>
                <div className="mt-10 grid w-full gap-3 sm:grid-cols-2">
                  {SUGGESTIONS.map(({ icon: Icon, text }) => (
                    <button
                      key={text}
                      type="button"
                      onClick={() => ask(text)}
                      className="group flex items-start gap-3 rounded-2xl border border-line bg-surface p-4 text-left text-sm font-medium shadow-[0_1px_2px_rgba(26,24,56,0.04)] transition hover:-translate-y-0.5 hover:border-brand/40 hover:shadow-[0_8px_24px_-12px_rgba(108,92,245,0.35)]"
                    >
                      <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-brand-soft text-brand">
                        <Icon className="h-4 w-4" />
                      </span>
                      <span className="pt-1.5">{text}</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-8">
                {messages.map((m, i) =>
                  m.role === 'user' ? (
                    <div key={i} className="flex justify-end">
                      <p className="max-w-[80%] rounded-2xl rounded-br-md bg-brand px-4 py-2.5 text-[15px] text-white">
                        {m.content}
                      </p>
                    </div>
                  ) : (
                    <Answer key={i} content={m.content} sources={m.sources ?? []} />
                  ),
                )}

                {loading && (
                  <div aria-live="polite" className="flex gap-4">
                    <Mark size="h-8 w-8" />
                    <div className="flex-1 pt-1">
                      <p className="text-sm font-medium text-muted">
                        Reading {documents.length} documents…
                      </p>
                      <div className="mt-3 space-y-2 motion-safe:animate-pulse">
                        <div className="h-3 w-11/12 rounded-full bg-line" />
                        <div className="h-3 w-4/5 rounded-full bg-line" />
                        <div className="h-3 w-3/5 rounded-full bg-line" />
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </main>

        <form onSubmit={handleSubmit} className="px-5 pb-5">
          <div className="mx-auto flex max-w-3xl items-end gap-2 rounded-2xl border border-line bg-surface p-2 pl-5 shadow-[0_8px_30px_-12px_rgba(26,24,56,0.18)] focus-within:border-brand/50">
            <label htmlFor="question" className="sr-only">
              Your question
            </label>
            <textarea
              id="question"
              rows={1}
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about your PDFs…"
              className="max-h-40 flex-1 resize-none bg-transparent py-2.5 text-[15px] outline-none placeholder:text-muted/70"
            />
            <button
              type="submit"
              aria-label="Ask"
              disabled={loading || !question.trim()}
              className="grid h-10 w-10 place-items-center rounded-xl bg-brand text-white transition hover:bg-[#5a4ae6] disabled:bg-line disabled:text-muted"
            >
              <SendIcon className="h-5 w-5" />
            </button>
          </div>
          <p className="mt-2 text-center text-xs text-muted">
            Answers come only from your library. Always check the cited pages.
          </p>
        </form>
      </div>
    </div>
  )
}