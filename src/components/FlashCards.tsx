import { useState, useEffect } from 'react'

interface FlashCard {
  front: string
  back: string
  type?: string
  tags?: string[]
}

interface FlashCardsProps {
  onClose: () => void
  lectureTitle: string
  lectureId: string
  cachedFlashcards?: FlashCard[] | null
}

const FlashCards = ({ onClose, lectureTitle, lectureId, cachedFlashcards }: FlashCardsProps) => {
  const [flashcards, setFlashcards] = useState<FlashCard[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isFlipped, setIsFlipped] = useState(false)
  const [knownCards, setKnownCards] = useState<Set<number>>(new Set())
  const [unknownCards, setUnknownCards] = useState<Set<number>>(new Set())

  useEffect(() => {
    const loadFlashcards = () => {
      try {
        setLoading(true)

        // If we have cached flashcards, use them
        if (cachedFlashcards && cachedFlashcards.length > 0) {
          console.log('Using cached flashcards:', cachedFlashcards.length)
          setFlashcards(cachedFlashcards)
          setLoading(false)
          return
        }

        // Otherwise show error - flashcards should be generated via chat
        setError('No flashcards available. Please generate flashcards through the chat first.')
        setLoading(false)
      } catch (err) {
        console.error('Error loading flashcards:', err)
        setError('Failed to load flashcards.')
        setLoading(false)
      }
    }

    loadFlashcards()
  }, [lectureId, cachedFlashcards])

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center p-4">
        <div className="glass rounded-3xl shadow-elegant-lg p-12 border border-white/20">
          <div className="flex flex-col items-center space-y-4">
            <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-white text-lg font-semibold">Loading flashcards...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error || flashcards.length === 0) {
    return (
      <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center p-4">
        <div className="glass rounded-3xl shadow-elegant-lg p-8 max-w-md border border-white/20">
          <div className="text-center">
            <div className="w-16 h-16 bg-red-500 rounded-full mx-auto mb-4 flex items-center justify-center">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Error Loading Flashcards</h3>
            <p className="text-white/80 mb-6">{error || 'Failed to load flashcards'}</p>
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

  const currentCard = flashcards[currentIndex]
  const isFirstCard = currentIndex === 0
  const isLastCard = currentIndex === flashcards.length - 1
  const progress = ((currentIndex + 1) / flashcards.length) * 100

  const handleFlip = () => {
    setIsFlipped(!isFlipped)
  }

  const handleNext = () => {
    if (!isLastCard) {
      setCurrentIndex(prev => prev + 1)
      setIsFlipped(false)
    }
  }

  const handlePrevious = () => {
    if (!isFirstCard) {
      setCurrentIndex(prev => prev - 1)
      setIsFlipped(false)
    }
  }

  const handleMarkKnown = () => {
    setKnownCards(prev => {
      const newSet = new Set(prev)
      newSet.add(currentIndex)
      return newSet
    })
    setUnknownCards(prev => {
      const newSet = new Set(prev)
      newSet.delete(currentIndex)
      return newSet
    })
  }

  const handleMarkUnknown = () => {
    setUnknownCards(prev => {
      const newSet = new Set(prev)
      newSet.add(currentIndex)
      return newSet
    })
    setKnownCards(prev => {
      const newSet = new Set(prev)
      newSet.delete(currentIndex)
      return newSet
    })
  }

  const isKnown = knownCards.has(currentIndex)
  const isUnknown = unknownCards.has(currentIndex)
  const knownCount = knownCards.size
  const unknownCount = unknownCards.size

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="glass rounded-3xl shadow-elegant-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-white/20 scrollbar-custom">
        {/* Header */}
        <div className="sticky top-0 glass border-b border-white/20 px-6 py-5 rounded-t-3xl backdrop-blur-xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-2xl font-bold gradient-text">Flashcards: {lectureTitle}</h2>
              <p className="text-sm text-white/80 mt-1 font-medium">
                Card {currentIndex + 1} of {flashcards.length}
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-xl transition-colors group"
              title="Close flashcards"
            >
              <svg className="w-6 h-6 text-white group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-white/20 rounded-full h-2.5 mb-3 overflow-hidden">
            <div
              className="bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 h-2.5 rounded-full transition-all duration-300 shadow-md"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Stats */}
          <div className="flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-2 px-3 py-1.5 bg-green-500/20 rounded-lg border border-green-400/30">
              <div className="w-3 h-3 rounded-full bg-green-400 shadow-sm"></div>
              <span className="text-white font-semibold">Known: {knownCount}</span>
            </div>
            <div className="flex items-center space-x-2 px-3 py-1.5 bg-red-500/20 rounded-lg border border-red-400/30">
              <div className="w-3 h-3 rounded-full bg-red-400 shadow-sm"></div>
              <span className="text-white font-semibold">Unknown: {unknownCount}</span>
            </div>
            <div className="flex items-center space-x-2 px-3 py-1.5 bg-white/10 rounded-lg border border-white/20">
              <div className="w-3 h-3 rounded-full bg-white/60 shadow-sm"></div>
              <span className="text-white/80 font-semibold">Not reviewed: {flashcards.length - knownCount - unknownCount}</span>
            </div>
          </div>
        </div>

        {/* Flashcard Content */}
        <div className="p-6 bg-white/5 backdrop-blur-sm flex flex-col pb-24">
          <div
            className="relative w-full h-[400px] perspective-1000 cursor-pointer mb-6"
            onClick={handleFlip}
          >
            <div
              className={`relative w-full h-full preserve-3d transition-transform duration-500 ${isFlipped ? 'rotate-y-180' : ''
                }`}
              style={{
                transformStyle: 'preserve-3d',
                transform: isFlipped ? 'rotateY(180deg)' : 'rotateY(0deg)'
              }}
            >
              {/* Front of card (Question) */}
              <div
                className={`absolute inset-0 w-full h-full backface-hidden rounded-3xl border-2 ${isUnknown
                  ? 'border-red-400 bg-gradient-to-br from-red-50 to-pink-50'
                  : isKnown
                    ? 'border-green-400 bg-gradient-to-br from-green-50 to-emerald-50'
                    : 'border-purple-400 bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50'
                  } p-8 flex flex-col items-center justify-center shadow-elegant-lg hover-lift`}
                style={{ backfaceVisibility: 'hidden' }}
              >
                <div className="text-center w-full">
                  <div className="mb-4">
                    <span className={`text-sm font-bold px-4 py-1.5 rounded-full shadow-md ${isUnknown
                      ? 'text-white bg-gradient-to-r from-red-400 to-pink-500'
                      : isKnown
                        ? 'text-white bg-gradient-to-r from-green-400 to-emerald-500'
                        : 'text-white bg-gradient-to-r from-purple-500 to-pink-500'
                      }`}>
                      Question
                    </span>
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-4 leading-relaxed">
                    {currentCard.front}
                  </h3>
                  <p className="text-gray-600 text-sm mt-4 font-medium">
                    👆 Click to flip
                  </p>
                </div>
              </div>

              {/* Back of card (Answer) */}
              <div
                className={`absolute inset-0 w-full h-full backface-hidden rounded-3xl border-2 ${isUnknown
                  ? 'border-red-400 bg-gradient-to-br from-red-50 to-pink-50'
                  : isKnown
                    ? 'border-green-400 bg-gradient-to-br from-green-50 to-emerald-50'
                    : 'border-orange-400 bg-gradient-to-br from-orange-50 via-pink-50 to-purple-50'
                  } p-8 flex flex-col items-center justify-center shadow-elegant-lg hover-lift rotate-y-180`}
                style={{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }}
              >
                <div className="text-center w-full">
                  <div className="mb-4">
                    <span className={`text-sm font-bold px-4 py-1.5 rounded-full shadow-md ${isUnknown
                      ? 'text-white bg-gradient-to-r from-red-400 to-pink-500'
                      : isKnown
                        ? 'text-white bg-gradient-to-r from-green-400 to-emerald-500'
                        : 'text-white bg-gradient-to-r from-orange-500 to-pink-500'
                      }`}>
                      Answer
                    </span>
                  </div>
                  <p className="text-lg text-gray-900 leading-relaxed font-medium">
                    {currentCard.back}
                  </p>
                  <p className="text-gray-600 text-sm mt-4 font-medium">
                    👆 Click to flip back
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons - Always visible when flipped */}
          {isFlipped && (
            <div className="flex space-x-3 animate-in fade-in slide-in-from-bottom z-10 relative">
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  handleMarkUnknown()
                }}
                className={`flex-1 px-6 py-3.5 rounded-xl border-2 transition-all font-semibold flex items-center justify-center space-x-2 hover-lift bg-white/95 backdrop-blur-sm shadow-elegant-lg ${isUnknown
                  ? 'border-red-500 bg-gradient-to-r from-red-100 to-pink-100 text-red-700'
                  : 'border-red-400 bg-white text-red-600 hover:bg-red-50 hover:border-red-500 hover:shadow-md'
                  }`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                <span>Mark as Unknown</span>
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  handleMarkKnown()
                }}
                className={`flex-1 px-6 py-3.5 rounded-xl border-2 transition-all font-semibold flex items-center justify-center space-x-2 hover-lift bg-white/95 backdrop-blur-sm shadow-elegant-lg ${isKnown
                  ? 'border-green-500 bg-gradient-to-r from-green-100 to-emerald-100 text-green-700'
                  : 'border-green-400 bg-white text-green-600 hover:bg-green-50 hover:border-green-500 hover:shadow-md'
                  }`}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span>Mark as Known</span>
              </button>
            </div>
          )}
        </div>

        {/* Navigation Footer */}
        <div className="sticky bottom-0 glass border-t border-white/20 px-6 py-4 rounded-b-3xl backdrop-blur-xl z-20">
          <div className="flex justify-between items-center">
            <button
              onClick={handlePrevious}
              disabled={isFirstCard}
              className="px-6 py-2.5 border-2 border-white/30 text-white rounded-xl hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-semibold flex items-center space-x-2 hover-lift disabled:hover:shadow-none"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span>Previous</span>
            </button>

            <div className="flex items-center space-x-2">
              <button
                onClick={handleFlip}
                className="px-6 py-2.5 bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 text-white rounded-xl hover:shadow-glow-purple transition-all font-semibold hover-lift"
              >
                {isFlipped ? 'Show Question' : 'Show Answer'}
              </button>
            </div>

            <button
              onClick={handleNext}
              disabled={isLastCard}
              className="px-6 py-2.5 border-2 border-white/30 text-white rounded-xl hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all font-semibold flex items-center space-x-2 hover-lift disabled:hover:shadow-none"
            >
              <span>Next</span>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default FlashCards

