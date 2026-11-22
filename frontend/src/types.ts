export type Source = {
  file: string
  page: number
  text: string
}

export type Message = {
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
}

export type DocumentInfo = {
  name: string
  chunks: number
}