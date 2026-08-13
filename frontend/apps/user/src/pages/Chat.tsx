import { useState } from "react"
import { Send, FileText } from "lucide-react"

export default function Chat() {
  const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string, sources?: string[] }[]>([])
  const [input, setInput] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    setMessages([...messages, { role: 'user', content: input }])
    
    // Simulate assistant response
    setTimeout(() => {
      setMessages(prev => [...prev, {
        role: 'assistant', 
        content: `Here is some information regarding "${input}". The library timings are 8 AM to 10 PM.`,
        sources: ["Student Handbook.pdf", "Library Guidelines.pdf"]
      }])
    }, 1000)
    
    setInput("")
  }

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900">
      <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-2xl mx-auto space-y-8">
            <h1 className="text-4xl font-semibold text-gray-800 dark:text-gray-100">
              How can CampusAI help you today?
            </h1>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full text-sm">
              <button onClick={() => setInput("What are the library timings?")} className="p-4 border rounded-xl hover:bg-gray-50 text-left dark:border-gray-800 dark:hover:bg-gray-800">
                <span className="block font-medium">Library Timings</span>
                <span className="text-gray-500">What are the library timings?</span>
              </button>
              <button onClick={() => setInput("Show my department information.")} className="p-4 border rounded-xl hover:bg-gray-50 text-left dark:border-gray-800 dark:hover:bg-gray-800">
                <span className="block font-medium">Department Info</span>
                <span className="text-gray-500">Show my department information.</span>
              </button>
              <button onClick={() => setInput("What clubs are available?")} className="p-4 border rounded-xl hover:bg-gray-50 text-left dark:border-gray-800 dark:hover:bg-gray-800">
                <span className="block font-medium">Clubs</span>
                <span className="text-gray-500">What clubs are available?</span>
              </button>
              <button onClick={() => setInput("What are the bus routes?")} className="p-4 border rounded-xl hover:bg-gray-50 text-left dark:border-gray-800 dark:hover:bg-gray-800">
                <span className="block font-medium">Transport</span>
                <span className="text-gray-500">What are the bus routes?</span>
              </button>
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : ''}`}>
                <div className={`p-4 rounded-2xl max-w-[85%] ${
                  msg.role === 'user' 
                    ? 'bg-gray-100 dark:bg-gray-800' 
                    : 'bg-transparent'
                }`}>
                  <p className="whitespace-pre-wrap">{msg.content}</p>
                  
                  {msg.sources && (
                    <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-800">
                      <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Sources</p>
                      <div className="flex flex-wrap gap-2">
                        {msg.sources.map(src => (
                          <div key={src} className="flex items-center gap-1.5 px-2.5 py-1.5 bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-md text-xs font-medium text-gray-700 dark:text-gray-300">
                            <FileText className="h-3 w-3" />
                            {src}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="p-4 md:p-6 pb-8 border-t border-gray-100 dark:border-gray-800">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto relative flex items-end shadow-sm border border-gray-300 dark:border-gray-700 rounded-2xl bg-white dark:bg-gray-900 overflow-hidden focus-within:ring-2 focus-within:ring-primary focus-within:border-primary transition-all">
          <textarea 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask CampusAI..."
            className="w-full max-h-48 min-h-[56px] py-4 pl-4 pr-12 resize-none bg-transparent outline-none disabled:opacity-50"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          <button 
            type="submit" 
            disabled={!input.trim()}
            className="absolute right-2 bottom-2 p-2 rounded-xl bg-primary text-primary-foreground disabled:opacity-50 disabled:bg-gray-200 disabled:text-gray-500 transition-colors"
          >
            <Send className="h-5 w-5" />
          </button>
        </form>
        <p className="text-center text-xs text-gray-500 mt-3">
          CampusAI can make mistakes. Verify important academic information.
        </p>
      </div>
    </div>
  )
}
