// The app mark: a rounded square with an open book.
export function Mark({ size = 'h-9 w-9' }: { size?: string }) {
  return (
    <span className={`grid shrink-0 place-items-center rounded-xl bg-brand text-white ${size}`}>
      <svg viewBox="0 0 24 24" className="h-[55%] w-[55%]" fill="none" stroke="currentColor" strokeWidth={2.2} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M12 6.5C10 5 7.5 4.5 4 5v13c3.5-.5 6 0 8 1.5 2-1.5 4.5-2 8-1.5V5c-3.5-.5-6 0-8 1.5z" />
        <path d="M12 6.5v13" />
      </svg>
    </span>
  )
}

export default function Logo({ light = false }: { light?: boolean }) {
  return (
    <span className="flex items-center gap-2.5">
      <Mark />
      <span className={`text-lg font-extrabold tracking-tight ${light ? 'text-white' : 'text-ink'}`}>
        StudyMate
      </span>
    </span>
  )
}