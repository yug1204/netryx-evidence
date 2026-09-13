import { useState, useRef, useEffect } from 'react'
import { Bot, Send, User, Layers, Search, Code, Paperclip } from 'lucide-react'

type Message = {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations?: { id: string; filename: string }[]
  isStreaming?: boolean
}

export default function AIAssistantPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'msg-0',
      role: 'assistant',
      content: 'Hello Investigator. I am the NETRYX Evidence AI. I have access to all uploaded documents, emails, and extracted IOCs in this case through vector similarity search. How can I assist you with your investigation today?',
    },
  ])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsTyping(true)

    // Simulate Network Request and SSE Stream
    setTimeout(() => {
      setIsTyping(false)
      const assistantMessageId = (Date.now() + 1).toString()
      
      setMessages((prev) => [
        ...prev,
        {
          id: assistantMessageId,
          role: 'assistant',
          content: '',
          isStreaming: true,
          citations: [
            { id: 'ev-142', filename: 'wire_instructions.pdf' },
            { id: 'ev-145', filename: 'email_01.eml' }
          ]
        },
      ])

      const responseWords = [
        "Based", "on", "the", "evidence", "found", "in", "this", "case,", "it", 
        "appears", "that", "the", "IP", "address", "**192.168.100.45**", "communicated", 
        "with", "a", "known", "malicious", "domain.", "\n\n", "The", "email", "header", 
        "analysis", "also", "shows", "a", "failed", "DMARC", "check,", "indicating", 
        "a", "highly", "probable", "spear-phishing", "attack."
      ]

      let currentText = ''
      responseWords.forEach((word, index) => {
        setTimeout(() => {
          currentText += word + ' '
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, content: currentText, isStreaming: index !== responseWords.length - 1 }
                : msg
            )
          )
        }, index * 80) // 80ms delay per word to simulate streaming
      })
    }, 1000)
  }

  return (
    <div className="animate-in" style={{ height: 'calc(100vh - var(--header-height) - 4rem)', display: 'flex', gap: 'var(--space-6)' }}>
      {/* Main Chat Area */}
      <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}>
        
        {/* Chat Header */}
        <div style={{ padding: 'var(--space-4) var(--space-6)', borderBottom: '1px solid var(--color-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div className="flex items-center gap-3">
            <div style={{ width: 36, height: 36, borderRadius: 'var(--radius-md)', background: 'rgba(56, 132, 255, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#3884ff' }}>
              <Bot size={20} />
            </div>
            <div>
              <h2 style={{ fontSize: 'var(--text-lg)', fontWeight: 700 }}>NETRYX AI Assistant</h2>
              <div style={{ fontSize: 'var(--text-xs)', color: 'var(--color-accent-green)', display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--color-accent-green)', display: 'inline-block' }} />
                RAG Engine Online — Connected to pgvector
              </div>
            </div>
          </div>
          
          <div className="flex gap-2">
            <button className="btn btn-secondary btn-sm"><Search size={14}/> Search History</button>
            <button className="btn btn-secondary btn-sm"><Layers size={14}/> Case #I042</button>
          </div>
        </div>

        {/* Chat Messages */}
        <div style={{ flex: 1, overflowY: 'auto', padding: 'var(--space-6)', display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
          {messages.map((msg) => (
            <div key={msg.id} style={{ display: 'flex', gap: 'var(--space-4)', flexDirection: msg.role === 'user' ? 'row-reverse' : 'row' }}>
              
              {/* Avatar */}
              <div style={{ 
                width: 32, height: 32, borderRadius: '50%', flexShrink: 0,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: msg.role === 'user' ? 'linear-gradient(135deg, var(--color-primary), var(--color-accent-cyan))' : 'rgba(56, 132, 255, 0.1)',
                color: msg.role === 'user' ? '#fff' : '#3884ff'
              }}>
                {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
              </div>

              {/* Message Bubble */}
              <div style={{ maxWidth: '75%', display: 'flex', flexDirection: 'column', gap: 'var(--space-2)', alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                
                <div style={{
                  padding: 'var(--space-3) var(--space-4)',
                  borderRadius: 'var(--radius-lg)',
                  background: msg.role === 'user' ? 'var(--color-primary)' : 'var(--color-bg-tertiary)',
                  border: msg.role === 'user' ? 'none' : '1px solid var(--color-border)',
                  color: msg.role === 'user' ? '#fff' : 'var(--color-text)',
                  fontSize: 'var(--text-sm)',
                  lineHeight: 1.6,
                  whiteSpace: 'pre-wrap',
                }}>
                  {msg.content}
                  {msg.isStreaming && <span className="blinking-cursor">|</span>}
                </div>

                {/* Citations */}
                {msg.citations && msg.citations.length > 0 && !msg.isStreaming && (
                  <div className="flex gap-2 mt-1 flex-wrap">
                    {msg.citations.map((cite, i) => (
                      <div key={i} style={{ 
                        display: 'flex', alignItems: 'center', gap: 4, 
                        padding: '2px 8px', borderRadius: 'var(--radius-full)', 
                        background: 'rgba(56, 132, 255, 0.1)', border: '1px solid rgba(56, 132, 255, 0.2)',
                        fontSize: '11px', color: '#3884ff', cursor: 'pointer'
                      }}>
                        <Paperclip size={10} />
                        {cite.filename}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div style={{ display: 'flex', gap: 'var(--space-4)', alignItems: 'center' }}>
              <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'rgba(56, 132, 255, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#3884ff' }}>
                <Bot size={16} />
              </div>
              <div style={{ color: 'var(--color-text-muted)', fontSize: 'var(--text-sm)' }}>
                Vectorizing query and searching context...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div style={{ padding: 'var(--space-4) var(--space-6)', borderTop: '1px solid var(--color-border)' }}>
          <div style={{ 
            display: 'flex', alignItems: 'center', gap: 'var(--space-3)', 
            background: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-lg)', padding: 'var(--space-2)' 
          }}>
            <button className="btn btn-secondary" style={{ padding: 8, background: 'transparent', border: 'none' }}>
              <Code size={18} />
            </button>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask a question about the evidence in this case (e.g., 'What IPs did the phishing email originate from?')"
              style={{
                flex: 1, background: 'transparent', border: 'none', color: 'var(--color-text)',
                fontSize: 'var(--text-sm)', outline: 'none'
              }}
            />
            <button 
              className="btn btn-primary" 
              onClick={handleSend}
              disabled={!input.trim() || isTyping}
              style={{ padding: '8px 12px' }}
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
