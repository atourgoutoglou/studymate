import { useState } from 'react'
import type { DocumentInfo } from '../types'
import Logo from './Logo'
import { FileIcon, PlusIcon, UploadIcon } from './Icons'
import ThemeToggle from './ThemeToggle'
import type { Theme } from '../useTheme'

type Props = {
  documents: DocumentInfo[]
  uploading: boolean
  error: string | null
  onUpload: (file: File) => void
  onNewChat: () => void
  theme: Theme
  onToggleTheme: () => void
}

export default function Sidebar({ documents, uploading, error, onUpload, onNewChat, theme, onToggleTheme }: Props) {
  const [dragging, setDragging] = useState(false)

  function handleFiles(files: FileList | null) {
    const file = files?.[0]
    if (file) onUpload(file)
  }

  return (
    <aside className="hidden w-72 shrink-0 flex-col bg-night text-white md:flex">
      <div className="px-5 pt-6">
        <Logo light />
        <button
          type="button"
          onClick={onNewChat}
          className="mt-6 flex w-full items-center justify-center gap-2 rounded-xl bg-white/10 py-2.5 text-sm font-semibold hover:bg-white/15"
        >
          <PlusIcon className="h-4 w-4" />
          New chat
        </button>
      </div>

      <div className="mt-8 flex-1 overflow-y-auto px-5">
        <div className="flex items-baseline justify-between px-1">
          <h2 className="text-sm font-semibold text-white/90">Library</h2>
          <span className="text-xs text-white/50">{documents.length} files</span>
        </div>

        <ul className="mt-3 space-y-1">
          {documents.map((doc) => (
            <li key={doc.name} className="flex items-center gap-3 rounded-xl px-2 py-2 hover:bg-white/5">
              <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-white/10 text-[#b9b1ff]">
                <FileIcon className="h-[18px] w-[18px]" />
              </span>
              <div className="min-w-0">
                <p className="truncate text-sm font-medium" title={doc.name}>
                  {doc.name.replace(/\.pdf$/i, '').replaceAll('_', ' ')}
                </p>
                <p className="text-xs text-white/50">{doc.chunks} passages indexed</p>
              </div>
            </li>
          ))}
        </ul>

        <label
          onDragOver={(e) => {
            e.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault()
            setDragging(false)
            handleFiles(e.dataTransfer.files)
          }}
          className={`mt-4 flex cursor-pointer items-center gap-3 rounded-xl border border-dashed px-3 py-3 transition-colors focus-within:outline-2 focus-within:outline-brand ${
            dragging ? 'border-[#b9b1ff] bg-white/10' : 'border-white/20 hover:border-white/40 hover:bg-white/5'
          }`}
        >
          <input
            type="file"
            accept=".pdf"
            className="sr-only"
            disabled={uploading}
            onChange={(e) => {
              handleFiles(e.target.files)
              e.target.value = ''
            }}
          />
          <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-brand">
            <UploadIcon className={`h-4 w-4 ${uploading ? 'motion-safe:animate-bounce' : ''}`} />
          </span>
          <span>
            <span className="block text-sm font-semibold">
              {uploading ? 'Indexing your PDF…' : 'Upload a PDF'}
            </span>
            <span className="block text-xs text-white/50">
              {uploading ? 'This can take a minute' : 'or drop it here'}
            </span>
          </span>
        </label>

        {error && (
          <p role="alert" className="mt-3 rounded-lg bg-red-500/15 px-3 py-2 text-xs text-red-200">
            {error}
          </p>
        )}
      </div>

    <div className="m-5 flex items-center gap-2">
        <div className="flex flex-1 items-center gap-2 rounded-xl bg-white/5 px-3 py-2.5 text-xs text-white/60">
            <span className="h-2 w-2 shrink-0 rounded-full bg-emerald-400" />
            Private, runs on your PC
        </div>
        <ThemeToggle
          theme={theme}
          onToggle={onToggleTheme}
          className="bg-white/5 text-white/80 hover:bg-white/15 hover:text-white"
        />
    </div>
    </aside>
  )
}