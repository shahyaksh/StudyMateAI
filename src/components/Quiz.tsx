import { useState, useEffect } from 'react'
import { apiService } from '../services/api'

interface QuizQuestion {
  question: string
  options: { A: string; B: string; C: string; D: string;[key: string]: string }
  correct_answer: string
  explanation?: string
  difficulty?: string
  topic?: string
}

interface QuizProps {
  onClose: () => void
  lectureTitle: string
  lectureId: string
  cachedQuestions?: QuizQuestion[] | null
}

const Quiz = ({ onClose, lectureTitle, lectureId, cachedQuestions }: QuizProps) => {
  const [questions, setQuestions] = useState<QuizQuestion[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [selectedAnswers, setSelectedAnswers] = useState<{ [key: number]: string }>({})
  const [showResults, setShowResults] = useState(false)
  const [showExplanation, setShowExplanation] = useState(false)

  useEffect(() => {
    const fetchQuiz = async () => {
      try {
        setLoading(true)

        // If we have cached questions, use them
        if (cachedQuestions && cachedQuestions.length > 0) {
          console.log('Using cached quiz questions:', cachedQuestions.length)
          setQuestions(cachedQuestions)
          setLoading(false)
          return
        }

        // Otherwise fetch from API
        console.log('Fetching quiz from API')
        const response = await apiService.generateQuiz({
          lectureId,
          numQuestions: 10
        })

        if (response.questions && response.questions.length > 0) {
          setQuestions(response.questions)
        } else {
          setError('No questions were generated. Please try again.')
        }
      } catch (err) {
        console.error('Error fetching quiz:', err)
        setError('Failed to load quiz. Please try again.')
      } finally {
        setLoading(false)
      }
    }

    fetchQuiz()
  }, [lectureId, cachedQuestions])

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center p-4">
        <div className="glass rounded-3xl shadow-elegant-lg p-12 border border-white/20">
          <div className="flex flex-col items-center space-y-4">
            <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-white text-lg font-semibold">Generating quiz questions...</p>
            <p className="text-white/70 text-sm">This may take a moment</p>
          </div>
        </div>
      </div>
    )
  }

  if (error || questions.length === 0) {
    return (
      <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center p-4">
        <div className="glass rounded-3xl shadow-elegant-lg p-8 max-w-md border border-white/20">
          <div className="text-center">
            <div className="w-16 h-16 bg-red-500 rounded-full mx-auto mb-4 flex items-center justify-center">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Error Loading Quiz</h3>
            <p className="text-white/80 mb-6">{error || 'Failed to load quiz questions'}</p>
            <button
              onClick={onClose}
              className="px-6 py-3 bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 text-white rounded-xl hover:shadow-glow-purple transition-all font-semibold"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    )
  }

  const currentQuestion = questions[currentQuestionIndex]
  const isLastQuestion = currentQuestionIndex === questions.length - 1
  const isFirstQuestion = currentQuestionIndex === 0
  const optionKeys = ['A', 'B', 'C', 'D'] as const

  const handleAnswerSelect = (optionKey: string, e?: React.MouseEvent) => {
    if (showResults) return
    if (e) {
      e.preventDefault()
      e.stopPropagation()
    }
    setSelectedAnswers(prev => ({
      ...prev,
      [currentQuestionIndex]: optionKey
    }))
    setShowExplanation(true)
  }

  const handleNext = () => {
    if (isLastQuestion) {
      setShowResults(true)
    } else {
      setCurrentQuestionIndex(prev => prev + 1)
      setShowExplanation(false)
    }
  }

  const handlePrevious = () => {
    if (!isFirstQuestion) {
      setCurrentQuestionIndex(prev => prev - 1)
      setShowExplanation(false)
    }
  }

  const handleSubmit = () => {
    setShowResults(true)
  }

  const calculateScore = () => {
    let correct = 0
    questions.forEach((question, index) => {
      if (selectedAnswers[index] === question.correct_answer) {
        correct++
      }
    })
    return { correct, total: questions.length }
  }

  const score = calculateScore()
  const percentage = Math.round((score.correct / score.total) * 100)

  if (showResults) {
    return (
      <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center p-4">
        <div className="glass rounded-3xl shadow-elegant-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-white/20 scrollbar-custom">
          <div className="p-8">
            <div className="text-center mb-8">
              <div className={`w-24 h-24 rounded-full mx-auto mb-6 flex items-center justify-center shadow-elegant-lg ${percentage >= 80 ? 'bg-gradient-to-br from-green-400 to-emerald-500' : percentage >= 60 ? 'bg-gradient-to-br from-yellow-400 to-orange-500' : 'bg-gradient-to-br from-red-400 to-pink-500'
                }`}>
                <span className="text-4xl font-bold text-white">
                  {percentage}%
                </span>
              </div>
              <h2 className="text-3xl font-bold gradient-text mb-3">Quiz Complete! 🎉</h2>
              <p className="text-lg text-white/90 font-medium">
                You scored {score.correct} out of {score.total} {score.total === 1 ? 'question' : 'questions'}
              </p>
            </div>

            <div className="space-y-4 mb-8">
              {questions.map((question, index) => {
                const userAnswer = selectedAnswers[index]
                const isCorrect = userAnswer === question.correct_answer
                return (
                  <div
                    key={index}
                    className={`p-5 rounded-2xl border-2 hover-lift transition-all ${isCorrect ? 'border-green-300 bg-gradient-to-br from-green-50 to-emerald-50 shadow-elegant' : 'border-red-300 bg-gradient-to-br from-red-50 to-pink-50 shadow-elegant'
                      }`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <p className="font-bold text-gray-900 text-lg">
                        Question {index + 1}: {question.question}
                      </p>
                      {isCorrect ? (
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-green-400 to-emerald-500 flex items-center justify-center flex-shrink-0 ml-2 shadow-md">
                          <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        </div>
                      ) : (
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-red-400 to-pink-500 flex items-center justify-center flex-shrink-0 ml-2 shadow-md">
                          <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                          </svg>
                        </div>
                      )}
                    </div>
                    <div className="mt-3 space-y-2">
                      <p className={`text-sm font-semibold ${isCorrect ? 'text-green-700' : 'text-red-700'}`}>
                        Your answer: {userAnswer ? question.options[userAnswer] : 'Not answered'}
                      </p>
                      {!isCorrect && (
                        <p className="text-sm text-gray-700 font-medium">
                          ✓ Correct answer: {question.options[question.correct_answer]}
                        </p>
                      )}
                      {question.explanation && (
                        <div className="mt-3 p-3 bg-white/60 rounded-lg border border-white/40">
                          <p className="text-sm text-gray-700 italic">
                            💡 {question.explanation}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>

            <div className="flex space-x-4">
              <button
                onClick={onClose}
                className="flex-1 px-6 py-3.5 bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 text-white rounded-xl hover:shadow-glow-purple transition-all duration-200 font-semibold hover-lift"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="glass rounded-3xl shadow-elegant-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto border border-white/20 scrollbar-custom">
        {/* Header */}
        <div className="sticky top-0 glass border-b border-white/20 px-6 py-5 rounded-t-3xl backdrop-blur-xl">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold gradient-text">Quiz: {lectureTitle}</h2>
              <p className="text-sm text-white/80 mt-1 font-medium">
                Question {currentQuestionIndex + 1} of {questions.length}
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-xl transition-colors group"
              title="Close quiz"
            >
              <svg className="w-6 h-6 text-white group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          {/* Progress Bar */}
          <div className="mt-4 w-full bg-white/20 rounded-full h-2.5 overflow-hidden">
            <div
              className="bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 h-2.5 rounded-full transition-all duration-300 shadow-md"
              style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Question Content */}
        <div className="p-6 bg-white/5 backdrop-blur-sm">
          <div className="mb-6">
            <h3 className="text-xl font-bold text-white mb-6 leading-relaxed">
              {currentQuestion.question}
            </h3>

            <div className="space-y-3">
              {optionKeys.map((key) => {
                const isSelected = selectedAnswers[currentQuestionIndex] === key
                const isCorrect = key === currentQuestion.correct_answer
                const showCorrect = showExplanation && isSelected

                return (
                  <button
                    key={`option-${currentQuestionIndex}-${key}`}
                    type="button"
                    onClick={(e) => handleAnswerSelect(key, e)}
                    disabled={showResults || showExplanation}
                    className={`w-full text-left p-4 rounded-xl border-2 transition-all hover-lift relative z-10 ${isSelected
                      ? showCorrect
                        ? 'border-green-400 bg-gradient-to-r from-green-50 to-emerald-50 shadow-elegant'
                        : 'border-purple-400 bg-gradient-to-r from-purple-50 to-pink-50 shadow-elegant'
                      : 'border-white/30 bg-white/10 hover:border-purple-400 hover:bg-white/20'
                      } ${showExplanation && isCorrect ? 'border-green-400 bg-gradient-to-r from-green-50 to-emerald-50' : ''} ${showResults || showExplanation ? 'cursor-default' : 'cursor-pointer'}`}
                  >
                    <div className="flex items-center pointer-events-none">
                      <div className={`w-7 h-7 rounded-full border-2 mr-3 flex items-center justify-center flex-shrink-0 transition-all ${isSelected
                        ? showCorrect
                          ? 'border-green-500 bg-gradient-to-br from-green-400 to-emerald-500'
                          : 'border-purple-500 bg-gradient-to-br from-purple-500 to-pink-500'
                        : 'border-white/40'
                        } ${showExplanation && isCorrect ? 'border-green-500 bg-gradient-to-br from-green-400 to-emerald-500' : ''}`}>
                        {isSelected && (
                          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        )}
                        {!isSelected && showExplanation && isCorrect && (
                          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                      <span className="text-gray-900 font-medium">{currentQuestion.options[key]}</span>
                    </div>
                  </button>
                )
              })}
            </div>

            {showExplanation && currentQuestion.explanation && (
              <div className="mt-5 p-4 bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl shadow-elegant">
                <p className="text-sm text-blue-900 font-medium">
                  <span className="font-bold">💡 Explanation:</span> {currentQuestion.explanation}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Footer Navigation */}
        <div className="sticky bottom-0 glass border-t border-white/20 px-6 py-4 rounded-b-3xl backdrop-blur-xl">
          <div className="flex justify-between">
            <button
              onClick={handlePrevious}
              disabled={isFirstQuestion}
              className="px-6 py-2.5 border-2 border-white/30 text-white rounded-xl hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-semibold hover-lift disabled:hover:shadow-none"
            >
              Previous
            </button>
            {isLastQuestion ? (
              <button
                onClick={handleSubmit}
                disabled={selectedAnswers[currentQuestionIndex] === undefined}
                className="px-6 py-2.5 bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 text-white rounded-xl hover:shadow-glow-purple disabled:opacity-50 disabled:cursor-not-allowed transition-all font-semibold hover-lift disabled:hover:shadow-none"
              >
                Submit Quiz
              </button>
            ) : (
              <button
                onClick={handleNext}
                disabled={selectedAnswers[currentQuestionIndex] === undefined}
                className="px-6 py-2.5 bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 text-white rounded-xl hover:shadow-glow-purple disabled:opacity-50 disabled:cursor-not-allowed transition-all font-semibold hover-lift disabled:hover:shadow-none"
              >
                Next
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Quiz

