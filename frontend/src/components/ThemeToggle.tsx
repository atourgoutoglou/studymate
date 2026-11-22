import type { Theme } from '../useTheme'
import { MoonIcon, SunIcon } from './Icons'

type Props = {
  theme: Theme
  onToggle: () => void
  className?: string
}

export default function ThemeToggle({ theme, onToggle, className = '' }: Props) {
  const dark = theme === 'dark'
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-label={dark ? 'Switch to light mode' : 'Switch to dark mode'}
      title={dark ? 'Light mode' : 'Dark mode'}
      className={`grid h-9 w-9 shrink-0 place-items-center rounded-xl transition ${className}`}
    >
      {dark ? <SunIcon className="h-[18px] w-[18px]" /> : <MoonIcon className="h-[18px] w-[18px]" />}
    </button>
  )
}