import { useState, useRef, useEffect } from 'react'
import { apiService } from '../services/api'
import { FormattedMessage } from './FormattedMessage'


interface Message {
  role: 'user' | 'assistant'
  content: string
  hasQuizLink?: boolean
  hasFlashCardLink?: boolean
}

interface ChatbotProps {
  lectureId?: string
  currentVideoTime?: number
  onOpenQuiz: (questions?: any[]) => void
  onOpenFlashCards: (flashcards?: any[]) => void
}

const Chatbot = ({ lectureId, currentVideoTime, onOpenQuiz, onOpenFlashCards }: ChatbotProps) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I\'m here to help you with questions about this lecture. I can reference the transcript and PDF materials. What would you like to know?'
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Reset session when lecture changes
  useEffect(() => {
    apiService.resetSession()
    setMessages([
      {
        role: 'assistant',
        content: 'Hello! I\'m here to help you with questions about this lecture. I can reference the transcript and PDF materials. What would you like to know?'
      }
    ])
  }, [lectureId])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userInput = input.trim()
    const userMessage: Message = { role: 'user', content: userInput }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      // Always make API call - let backend LLM determine intent
      const response = await apiService.chat(
        userInput,
        lectureId,
        currentVideoTime
      )

      // Check if backend determined this is a quiz or flashcard request
      const isQuizIntent = response.intent === 'quiz'
      const isFlashcardIntent = response.intent === 'flashcard'

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        hasQuizLink: isQuizIntent,
        hasFlashCardLink: isFlashcardIntent
      }
      setMessages(prev => [...prev, assistantMessage])

      // If quiz questions were generated, trigger the quiz modal with cached questions
      if (isQuizIntent && response.quiz_questions && response.quiz_questions.length > 0) {
        // Pass the generated questions to parent to open quiz
        onOpenQuiz(response.quiz_questions)
      }

      // If flashcards were generated, trigger the flashcard modal with cached cards
      if (isFlashcardIntent && response.flashcards && response.flashcards.length > 0) {
        // Pass the generated flashcards to parent to open flashcards
        onOpenFlashCards(response.flashcards)
      }

    } catch (error) {
      console.error('Error calling API:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your request. Please make sure the backend server is running on port 5001 and try again.'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] bg-white/10 backdrop-blur-xl">
      {/* Header */}
      <div className="px-6 py-5 border-b border-white/20 bg-gradient-to-r from-white/10 to-white/5">
        <div className="flex items-center space-x-4">
          <div className="relative">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500 flex items-center justify-center shadow-glow-purple animate-pulse-slow">
              <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white animate-ping"></div>
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Lecture Assistant</h2>
            <p className="text-sm text-white/80">Ask questions about the lecture content</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4 scrollbar-custom bg-gradient-to-b from-transparent via-white/5 to-transparent">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom duration-300`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-5 py-4 shadow-elegant ${message.role === 'user'
                ? 'bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500 text-white hover-lift'
                : 'bg-white/90 backdrop-blur-sm text-gray-900 border border-white/30 hover-lift'
                }`}
            >
              {message.role === 'assistant' && (
                <div className="flex items-center space-x-2 mb-3">
                  <div className="w-6 h-6 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 flex items-center justify-center">
                    <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <span className="text-xs font-semibold text-purple-600">AI Assistant</span>
                </div>
              )}
              <FormattedMessage content={message.content} role={message.role} />
              {message.hasQuizLink && onOpenQuiz && (
                <button
                  onClick={() => onOpenQuiz()}  // Don't pass questions when user clicks button
                  className="mt-4 w-full px-4 py-3 bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 text-white rounded-xl hover:shadow-glow-purple hover:scale-[1.02] transition-all duration-200 font-semibold flex items-center justify-center space-x-2 shadow-elegant hover-lift"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <span>Take Quiz</span>
                </button>
              )}
              {message.hasFlashCardLink && onOpenFlashCards && (
                <button
                  onClick={() => onOpenFlashCards()}  // Don't pass flashcards when user clicks button
                  className="mt-4 w-full px-4 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-xl hover:from-indigo-600 hover:to-purple-700 hover:shadow-lg transition-all duration-200 font-medium flex items-center justify-center space-x-2 hover-lift"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                  <span>Study Flashcards</span>
                </button>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start animate-in fade-in">
            <div className="bg-white/90 backdrop-blur-sm rounded-2xl px-5 py-4 shadow-elegant border border-white/30">
              <div className="flex space-x-2">
                <div className="w-3 h-3 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-3 h-3 bg-pink-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-3 h-3 bg-orange-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-6 py-5 border-t border-white/20 bg-white/10 backdrop-blur-xl">
        <div className="flex space-x-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about the lecture..."
              className="w-full px-5 py-3.5 pr-12 border-2 border-white/30 rounded-xl focus:outline-none focus:ring-2 focus:ring-purple-400/50 focus:border-purple-400 transition-all bg-white/90 backdrop-blur-sm text-gray-900 placeholder-gray-500 shadow-elegant hover-lift"
              disabled={isLoading}
            />
            <svg className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="px-6 py-3.5 bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 text-white rounded-xl hover:shadow-glow-purple disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-semibold flex items-center space-x-2 shadow-elegant hover-lift disabled:hover:shadow-none"
          >
            <span>Send</span>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}

export default Chatbot

