// API service for communicating with the backend
const API_BASE_URL = 'http://localhost:5001/api'

export interface ChatMessage {
    role: 'user' | 'assistant'
    content: string
}

export interface ChatResponse {
    session_id: string
    response: string
    intent: string
    citations: Array<{
        source: string
        timestamp?: string
        text: string
    }>
    metadata: Record<string, any>
    timestamp: string
    quiz_questions?: any[]  // Optional quiz questions if intent is 'quiz'
    flashcards?: any[]  // Optional flashcards if intent is 'flashcard'
}

export interface QuizResponse {
    questions: Array<{
        question: string
        options: { A: string; B: string; C: string; D: string }
        correct_answer: string
        explanation?: string
        difficulty?: string
        topic?: string
    }>
}

export interface FlashcardResponse {
    session_id: string
    flashcards_text: string
    flashcards: Array<{
        front: string
        back: string
    }>
    num_cards: number
    timestamp: string
}

class APIService {
    private sessionId: string | null = null

    async chat(query: string, lectureId?: string, timestamp?: number): Promise<ChatResponse> {
        try {
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query,
                    lecture_id: lectureId,
                    timestamp,
                    session_id: this.sessionId,
                }),
            })

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            const data: ChatResponse = await response.json()

            // Store session ID for conversation continuity
            if (data.session_id) {
                this.sessionId = data.session_id
            }

            return data
        } catch (error) {
            console.error('Chat API error:', error)
            throw error
        }
    }

    async generateQuiz(params: { lectureId: string; numQuestions?: number }): Promise<QuizResponse> {
        try {
            const response = await fetch(`${API_BASE_URL}/quiz`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    lecture_id: params.lectureId,
                    num_questions: params.numQuestions || 10,
                    session_id: this.sessionId,
                }),
            })

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            const data: QuizResponse = await response.json()
            return data
        } catch (error) {
            console.error('Quiz API error:', error)
            throw error
        }
    }

    async generateFlashcards(topic: string, numCards: number = 10, lectureId?: string): Promise<FlashcardResponse> {
        try {
            const response = await fetch(`${API_BASE_URL}/flashcards`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    topic,
                    num_cards: numCards,
                    lecture_id: lectureId,
                    session_id: this.sessionId,
                }),
            })

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            const data: FlashcardResponse = await response.json()
            return data
        } catch (error) {
            console.error('Flashcards API error:', error)
            throw error
        }
    }

    async healthCheck(): Promise<{ status: string; timestamp: string; active_sessions: number }> {
        try {
            const response = await fetch(`${API_BASE_URL}/health`)

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            return await response.json()
        } catch (error) {
            console.error('Health check error:', error)
            throw error
        }
    }

    resetSession() {
        this.sessionId = null
    }

    getSessionId(): string | null {
        return this.sessionId
    }
}

// Export a singleton instance
export const apiService = new APIService()
