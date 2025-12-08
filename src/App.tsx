import { useState, useRef, useEffect } from 'react'
import VideoPlayer, { VideoPlayerRef } from './components/VideoPlayer'
import ContentTabs from './components/ContentTabs'
import Chatbot from './components/Chatbot'
import SidePanel from './components/SidePanel'
import Quiz from './components/Quiz'
import FlashCards from './components/FlashCards'
import { loadLectures, getLectureById, Lecture } from './data/lectures'

function App() {
  const [activeTab, setActiveTab] = useState<'notes' | 'description' | 'transcript'>('transcript')
  const [currentVideoTime, setCurrentVideoTime] = useState(0)
  const [activeLectureId, setActiveLectureId] = useState<string>('lecture-7')
  const [isSidePanelOpen, setIsSidePanelOpen] = useState(true)
  const [showQuiz, setShowQuiz] = useState(false)
  const [showFlashCards, setShowFlashCards] = useState(false)
  const [cachedQuizQuestions, setCachedQuizQuestions] = useState<any[] | null>(null)
  const [cachedFlashcards, setCachedFlashcards] = useState<any[] | null>(null)
  const [lectures, setLectures] = useState<Lecture[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const videoPlayerRef = useRef<VideoPlayerRef>(null)

  // Load lectures from JSON on mount
  useEffect(() => {
    const fetchLectures = async () => {
      try {
        const data = await loadLectures()
        setLectures(data)
        setIsLoading(false)
      } catch (error) {
        console.error('Failed to load lectures:', error)
        setIsLoading(false)
      }
    }
    fetchLectures()
  }, [])

  const activeLecture = getLectureById(lectures, activeLectureId) || lectures[0]

  const handleTimestampClick = (timeInSeconds: number) => {
    if (videoPlayerRef.current) {
      videoPlayerRef.current.seekTo(timeInSeconds)
    }
  }

  const handleTimeUpdate = (currentTime: number) => {
    setCurrentVideoTime(currentTime)
  }

  const handleLectureSelect = (lectureId: string) => {
    setActiveLectureId(lectureId)
    setCurrentVideoTime(0)
    if (videoPlayerRef.current) {
      videoPlayerRef.current.seekTo(0)
    }
  }

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-pink-900 to-orange-900">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white text-xl font-semibold">Loading lectures...</p>
        </div>
      </div>
    )
  }

  // Show error state if no lectures loaded
  if (lectures.length === 0) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-900 via-pink-900 to-orange-900">
        <div className="text-center glass p-8 rounded-3xl max-w-md">
          <svg className="w-16 h-16 text-white mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h2 className="text-2xl font-bold text-white mb-2">No Lectures Found</h2>
          <p className="text-white/80">Unable to load lecture data. Please check the console for errors.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      {/* Side Panel */}
      <SidePanel
        lectures={lectures.map(l => ({
          id: l.id,
          title: l.title,
          session: l.session,
          description: l.description,
          duration: l.duration,
        }))}
        activeLectureId={activeLectureId}
        onLectureSelect={handleLectureSelect}
        isOpen={isSidePanelOpen}
        onToggle={() => setIsSidePanelOpen(!isSidePanelOpen)}
      />


      {/* Main Content */}
      <div className={`transition-all duration-300 ${isSidePanelOpen ? 'ml-80' : 'ml-0'}`}>
        {/* Header */}
        <header className="glass sticky top-0 z-50 shadow-elegant border-b border-white/20">
          <div className="max-w-screen-2xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              {/* Logo and Title */}
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setIsSidePanelOpen(!isSidePanelOpen)}
                  className="p-2 rounded-xl hover:bg-white/10 transition-all duration-300 hover-lift"
                  aria-label="Toggle sidebar"
                >
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  </svg>
                </button>

                {/* Logo and Brand */}
                <div className="flex items-center space-x-3">
                  <img
                    src="/studymateai-logo.png"
                    alt="StudyMateAI Logo"
                    className="w-10 h-10 object-contain"
                  />
                  <div>
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-orange-400 bg-clip-text text-transparent">
                      StudyMateAI
                    </h1>
                    <p className="text-xs text-white/60">Your AI Learning Companion</p>
                  </div>
                </div>
              </div>

              {/* Lecture Info */}
              <div className="hidden md:flex items-center space-x-4">
                <div className="text-right">
                  <h2 className="text-lg font-bold text-white">{activeLecture?.title}</h2>
                  <p className="text-sm text-white/70">{activeLecture?.session}</p>
                </div>
              </div>
            </div>
          </div>
        </header>

        <div className="max-w-[1920px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[calc(100vh-12rem)]">
            {/* Left Column - Video Player + Content Tabs */}
            <div className="lg:col-span-7 flex flex-col gap-6 min-h-0">
              {/* Video Player */}
              <div className="glass rounded-3xl shadow-elegant-lg overflow-hidden border border-white/20 flex-shrink-0 hover-lift">
                <div className="w-full h-[400px] bg-gradient-to-br from-gray-900 to-black relative">
                  {activeLecture && <VideoPlayer ref={videoPlayerRef} videoUrl={activeLecture.videoUrl} onTimeUpdate={handleTimeUpdate} />}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent pointer-events-none"></div>
                </div>
              </div>

              {/* Content Tabs */}
              <div className="glass rounded-3xl shadow-elegant-lg overflow-hidden border border-white/20 flex-1 flex flex-col min-h-0 hover-lift">
                {activeLecture && (
                  <ContentTabs
                    activeTab={activeTab}
                    onTabChange={setActiveTab}
                    transcript={activeLecture.transcript}
                    description={activeLecture.description}
                    notes={activeLecture.notes}
                    onTimestampClick={handleTimestampClick}
                    currentVideoTime={currentVideoTime}
                  />
                )}
              </div>
            </div>

            {/* Right Column - Chatbot */}
            <div className="lg:col-span-5 flex flex-col">
              <div className="glass rounded-3xl shadow-elegant-lg overflow-hidden border border-white/20 flex-1 flex flex-col hover-lift">
                <Chatbot
                  key={activeLectureId}
                  lectureId={activeLecture.id}
                  currentVideoTime={currentVideoTime}
                  onOpenQuiz={(questions) => {
                    if (questions && questions.length > 0) {
                      setCachedQuizQuestions(questions)
                    }
                    setShowQuiz(true)
                  }}
                  onOpenFlashCards={(flashcards) => {
                    if (flashcards && flashcards.length > 0) {
                      setCachedFlashcards(flashcards)
                    }
                    setShowFlashCards(true)
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      </div >

      {/* Quiz Modal */}
      {
        showQuiz && activeLecture && (
          <Quiz
            onClose={() => {
              setShowQuiz(false)
              setCachedQuizQuestions(null)  // Clear cache when closing
            }}
            lectureTitle={activeLecture.title}
            lectureId={activeLecture.id}
            cachedQuestions={cachedQuizQuestions}
          />
        )
      }

      {/* FlashCards Modal */}
      {
        showFlashCards && activeLecture && (
          <FlashCards
            onClose={() => {
              setShowFlashCards(false)
              setCachedFlashcards(null)  // Clear cache when closing
            }}
            lectureTitle={activeLecture.title}
            lectureId={activeLecture.id}
            cachedFlashcards={cachedFlashcards}
          />
        )
      }
    </div >
  )
}

export default App
