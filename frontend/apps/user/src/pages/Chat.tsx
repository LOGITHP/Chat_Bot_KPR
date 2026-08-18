import { useState, useRef, useEffect, useCallback } from "react"
import { Send, FileText, Bot, User, RotateCcw, Sparkles, AlertCircle } from "lucide-react"

/* ────────────────────────────────────────────────────────
   Types
──────────────────────────────────────────────────────── */
interface Source {
  filename?: string
  page?: number
  sheet?: string
  section?: string
}

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  sources?: Source[]
  error?: boolean
}

/* ────────────────────────────────────────────────────────
   Helpers
──────────────────────────────────────────────────────── */
function generateId() {
  return crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).slice(2)
}

const TOKEN_KEY         = "campus_ai_token"
const GUEST_SESSION_KEY = "campus_guest_session"

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem(TOKEN_KEY)
  const headers: HeadersInit = { "Content-Type": "application/json" }
  if (token) headers["Authorization"] = `Bearer ${token}`
  return headers
}

async function ensureGuestSession(fallbackId: string): Promise<string> {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) return fallbackId // authenticated — don't create guest session

  // Use existing guest session if available
  const existing = localStorage.getItem(GUEST_SESSION_KEY)
  if (existing) return existing

  try {
    const res = await fetch("/api/v1/chat/guest/session", { method: "POST" })
    if (res.ok) {
      const data = await res.json()
      localStorage.setItem(GUEST_SESSION_KEY, data.guest_session_id)
      return data.guest_session_id
    }
  } catch { /* fall through */ }
  return fallbackId
}

/* ────────────────────────────────────────────────────────
   Suggestion prompts
──────────────────────────────────────────────────────── */
const SUGGESTIONS = [
  { label: "Library Timings", prompt: "What are the library timings?" },
  { label: "Department Info", prompt: "Show my department information." },
  { label: "Available Clubs", prompt: "What clubs are available?" },
  { label: "Bus Routes", prompt: "What are the campus bus routes?" },
]

/* ────────────────────────────────────────────────────────
   Sub-components
──────────────────────────────────────────────────────── */
function TypingIndicator() {
  return (
    <div className="flex gap-3 animate-message-in">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 flex items-center justify-center shadow-md">
        <Bot className="w-4 h-4 text-white" />
      </div>
      <div className="px-4 py-3 rounded-2xl rounded-tl-sm bg-white dark:bg-[hsl(var(--chat-ai-bg))] border border-[hsl(var(--chat-ai-border))] shadow-sm">
        <div className="flex items-center gap-1.5 h-5 text-indigo-500 dark:text-indigo-400">
          <span className="typing-dot" />
          <span className="typing-dot" />
          <span className="typing-dot" />
        </div>
      </div>
    </div>
  )
}

function MessageBubble({ msg }: { msg: Message }) {
  const isUser = msg.role === "user"
  return (
    <div className={`flex gap-3 animate-message-in ${isUser ? "flex-row-reverse" : ""}`}>
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-md ${
        isUser
          ? "bg-gradient-to-br from-indigo-500 to-violet-600"
          : msg.error
            ? "bg-gradient-to-br from-red-400 to-rose-500"
            : "bg-gradient-to-br from-violet-500 to-indigo-600"
      }`}>
        {isUser ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
      </div>

      <div className={`max-w-[80%] space-y-2 ${isUser ? "items-end flex flex-col" : ""}`}>
        {/* Bubble */}
        <div className={`px-4 py-3 rounded-2xl shadow-sm text-sm leading-relaxed whitespace-pre-wrap ${
          isUser
            ? "bg-gradient-to-br from-indigo-500 to-violet-600 text-white rounded-tr-sm"
            : msg.error
              ? "bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800/50 text-red-700 dark:text-red-300 rounded-tl-sm"
              : "bg-white dark:bg-[hsl(var(--chat-ai-bg))] border border-[hsl(var(--chat-ai-border))] text-foreground rounded-tl-sm"
        }`}>
          {msg.error && <AlertCircle className="w-4 h-4 inline mr-1.5 -mt-0.5" />}
          {msg.content}
        </div>

        {/* Sources */}
        {msg.sources && msg.sources.length > 0 && (
          <div className="space-y-1.5">
            <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground pl-1">
              Sources
            </p>
            <div className="flex flex-wrap gap-1.5">
              {msg.sources.map((src, i) => (
                <div
                  key={i}
                  className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900/50 text-[11px] font-medium text-indigo-700 dark:text-indigo-300"
                >
                  <FileText className="w-3 h-3 flex-shrink-0" />
                  <span>
                    {src.filename || "Document"}
                    {src.page ? ` · p.${src.page}` : ""}
                    {src.sheet ? ` · ${src.sheet}` : ""}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

/* ────────────────────────────────────────────────────────
   Main Chat component
──────────────────────────────────────────────────────── */
export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const conversationIdRef = useRef<string>(generateId())
  const guestSessionInitialized = useRef(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-scroll on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isLoading])

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = "auto"
    ta.style.height = `${Math.min(ta.scrollHeight, 160)}px`
  }, [input])

  // Initialize guest session on mount (if no auth token)
  useEffect(() => {
    if (guestSessionInitialized.current) return
    guestSessionInitialized.current = true
    const isGuest = !localStorage.getItem(TOKEN_KEY)
    if (isGuest) {
      ensureGuestSession(conversationIdRef.current).then(id => {
        conversationIdRef.current = id
      })
    }
  }, [])

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isLoading) return

    const userMsg: Message = { id: generateId(), role: "user", content: text }
    setMessages(prev => [...prev, userMsg])
    setInput("")
    setIsLoading(true)

    const isGuest = !localStorage.getItem(TOKEN_KEY)

    try {
      const res = await fetch("/api/v1/chat/", {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({
          question: text,
          conversation_id: conversationIdRef.current,
          is_guest: isGuest,
        }),
      })

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.detail || `Server error ${res.status}`)
      }

      const data = await res.json()
      const assistantMsg: Message = {
        id: generateId(),
        role: "assistant",
        content: data.answer || "No response received.",
        sources: data.sources?.filter((s: Source) => s.filename) || [],
      }
      setMessages(prev => [...prev, assistantMsg])
    } catch (err: unknown) {
      const errMsg: Message = {
        id: generateId(),
        role: "assistant",
        content: err instanceof Error ? err.message : "Something went wrong. Please try again.",
        error: true,
      }
      setMessages(prev => [...prev, errMsg])
    } finally {
      setIsLoading(false)
    }
  }, [isLoading])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage(input)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  const handleRetry = () => {
    const lastUser = [...messages].reverse().find(m => m.role === "user")
    if (lastUser) sendMessage(lastUser.content)
  }

  /* ─── Render ─── */
  return (
    <div className="flex flex-col h-full bg-background">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          /* ── Welcome screen ── */
          <div className="h-full flex flex-col items-center justify-center p-6 animate-fade-in">
            {/* KPR Logo */}
            <div className="relative mb-6">
              <div className="w-24 h-24 rounded-2xl overflow-hidden shadow-xl ring-4 ring-indigo-500/20 bg-white flex items-center justify-center">
                <img
                  src="/kpr_logo.png"
                  alt="KPRIET Logo"
                  className="w-full h-full object-contain p-1"
                />
              </div>
              <div className="absolute -bottom-2 -right-2 w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-md">
                <Sparkles className="w-4 h-4 text-white" />
              </div>
            </div>
            <h1 className="text-3xl font-bold gradient-text mb-2 text-center">
              How can CampusAI help you?
            </h1>
            <p className="text-muted-foreground text-sm mb-10 text-center max-w-sm">
              Ask anything about campus life — departments, clubs, transport, and more.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-xl">
              {SUGGESTIONS.map(s => (
                <button
                  key={s.label}
                  onClick={() => sendMessage(s.prompt)}
                  disabled={isLoading}
                  className="group p-4 rounded-xl border border-border bg-card hover:border-indigo-300 dark:hover:border-indigo-700 hover:shadow-md hover:shadow-indigo-500/10 transition-all duration-200 text-left disabled:opacity-50"
                >
                  <span className="block text-sm font-semibold text-foreground group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                    {s.label}
                  </span>
                  <span className="block text-xs text-muted-foreground mt-0.5">{s.prompt}</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* ── Message thread ── */
          <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
            {messages.map(msg => (
              <MessageBubble key={msg.id} msg={msg} />
            ))}
            {isLoading && <TypingIndicator />}

            {/* Retry button after error */}
            {!isLoading && messages[messages.length - 1]?.error && (
              <div className="flex justify-center animate-fade-in">
                <button
                  onClick={handleRetry}
                  className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-950/30 rounded-lg transition-colors"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  Retry
                </button>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Bar */}
      <div className="flex-shrink-0 px-4 pb-6 pt-3 border-t border-border bg-background/80 backdrop-blur-sm">
        <form
          onSubmit={handleSubmit}
          className="max-w-3xl mx-auto relative flex items-end gap-2 glass rounded-2xl px-4 py-3 shadow-lg shadow-black/5 focus-within:ring-2 focus-within:ring-[hsl(var(--primary))] focus-within:ring-offset-1 transition-all"
        >
          <textarea
            ref={textareaRef}
            id="chat-input"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask CampusAI anything…"
            rows={1}
            disabled={isLoading}
            className="flex-1 resize-none bg-transparent outline-none text-sm text-foreground placeholder:text-muted-foreground min-h-[28px] max-h-40 py-0.5 disabled:opacity-60 leading-relaxed"
          />
          <button
            id="chat-send-btn"
            type="submit"
            disabled={!input.trim() || isLoading}
            className="flex-shrink-0 w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 text-white flex items-center justify-center shadow-md hover:shadow-indigo-500/30 hover:scale-105 active:scale-95 transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:shadow-none"
          >
            {isLoading ? (
              <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.4 0 0 5.4 0 12h4z"/>
              </svg>
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </form>
        <p className="text-center text-[11px] text-muted-foreground mt-2.5">
          CampusAI can make mistakes — verify important academic information.
        </p>
      </div>
    </div>
  )
}
