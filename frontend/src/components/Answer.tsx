import { useState } from 'react'
import type { ReactNode } from 'react'
import type { Source } from '../types'
import { Mark } from './Logo'
import { CheckIcon, CopyIcon } from './Icons'

// Finds citations like [rag_paper.pdf, page 3]
const CITATION = /\[([^\]]+?\.pdf), page (\d+)\]/g

type Props = {
  content: string
  sources: Source[]
}

// Replaces each citation with a small numbered badge.
// The number points to the matching source card.
// If the cited page was never retrieved, the badge turns amber with "?".
function renderWithCitations(content: string, sources: Source[]): ReactNode[] {
  const parts: ReactNode[] = []
  let last = 0

  for (const match of content.matchAll(CITATION)) {
    const [full, file, pageText] = match
    const page = Number(pageText)
    const start = match.index ?? 0
    const index = sources.findIndex((s) => s.file === file && s.page === page)
    const verified = index !== -1

    parts.push(content.slice(last, start).trimEnd())
    parts.push(
      <a
        key={start}
        href={verified ? `#source-${index}` : undefined}
        title={
          verified
            ? `${file}, page ${page}`
            : `${file}, page ${page} was not in the retrieved passages. Double-check this.`
        }
        className={`relative -top-1.5 mx-0.5 inline-grid h-[18px] min-w-[18px] place-items-center rounded-md px-1 text-[11px] font-bold no-underline ${
          verified
            ? 'bg-brand-soft text-brand hover:bg-brand hover:text-white'
            : 'bg-amber-100 text-amber-700 dark:bg-amber-400/20 dark:text-amber-300'
        }`}
      >
        {verified ? index + 1 : '?'}
      </a>,
    )
    last = start + full.length
  }
  parts.push(content.slice(last))
  return parts
}

export default function Answer({ content, sources }: Props) {
  const [copied, setCopied] = useState(false)
  const [showAll, setShowAll] = useState(false)
  const visible = showAll ? sources : sources.slice(0, 3)

  async function copy() {
    await navigator.clipboard.writeText(content.replace(CITATION, '').replace(/\s+([.,])/g, '$1'))
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }

  return (
    <div className="flex gap-4">
      <Mark size="h-8 w-8" />

      <div className="min-w-0 flex-1">
        {sources.length > 0 && (
          <div className="mb-5">
            <p className="mb-2 text-sm font-semibold text-muted">Sources</p>
            <div className="grid gap-2 sm:grid-cols-3">
              {visible.map((source, i) => (
                <div
                  key={i}
                  id={`source-${i}`}
                  className="scroll-mt-6 rounded-xl border border-line bg-surface p-3 target:border-brand target:ring-2 target:ring-brand-soft"
                >
                  <div className="flex items-center gap-2">
                    <span className="grid h-5 w-5 shrink-0 place-items-center rounded-md bg-brand-soft text-[11px] font-bold text-brand">
                      {i + 1}
                    </span>
                    <span className="truncate text-xs font-semibold" title={source.file}>
                      {source.file.replace(/\.pdf$/i, '').replaceAll('_', ' ')}
                    </span>
                  </div>
                  <p className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-muted">{source.text}</p>
                  <p className="mt-2 text-[11px] font-semibold text-brand">Page {source.page}</p>
                </div>
              ))}
            </div>
            {sources.length > 3 && (
              <button
                type="button"
                onClick={() => setShowAll(!showAll)}
                className="mt-2 text-xs font-semibold text-brand hover:underline"
              >
                {showAll ? 'Show fewer sources' : `Show all ${sources.length} sources`}
              </button>
            )}
          </div>
        )}

        <p className="text-[15.5px] leading-[1.8] whitespace-pre-wrap">
          {renderWithCitations(content, sources)}
        </p>

        <button
          type="button"
          onClick={copy}
          className="mt-3 -ml-2 flex items-center gap-1.5 rounded-lg px-2 py-1 text-xs font-semibold text-muted hover:bg-surface hover:text-ink"
        >
          {copied ? <CheckIcon className="h-3.5 w-3.5" /> : <CopyIcon className="h-3.5 w-3.5" />}
          {copied ? 'Copied' : 'Copy answer'}
        </button>
      </div>
    </div>
  )
}