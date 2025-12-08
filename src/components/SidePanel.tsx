export interface Lecture {
  id: string
  title: string
  session: string
  description: string
  duration: string
  thumbnail?: string
}

interface SidePanelProps {
  lectures: Lecture[]
  activeLectureId: string
  onLectureSelect: (lectureId: string) => void
  isOpen: boolean
  onToggle: () => void
}

const SidePanel = ({ lectures, activeLectureId, onLectureSelect, isOpen }: SidePanelProps) => {
  return (
    <>
      {/* Side Panel */}
      <div
        className={`fixed left-0 top-0 h-full glass border-r border-white/20 shadow-elegant-lg transition-all duration-300 z-30 ${isOpen ? 'translate-x-0 w-80' : '-translate-x-full w-80'
          }`}
      >
        <div className="h-full flex flex-col">
          {/* Header */}
          <div className="px-6 py-5 border-b border-white/20 bg-gradient-to-r from-white/10 to-white/5">
            <div className="flex items-center mb-3">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-glow-purple">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <h2 className="text-xl font-bold text-white">Lectures</h2>
              </div>
            </div>
            <p className="text-sm text-white/80 font-medium">{lectures.length} available sessions</p>
          </div>

          {/* Lecture List */}
          <div className="flex-1 overflow-y-auto scrollbar-custom p-4 space-y-3">
            {lectures.map((lecture) => {
              const isActive = lecture.id === activeLectureId
              return (
                <button
                  key={lecture.id}
                  onClick={() => onLectureSelect(lecture.id)}
                  className={`w-full text-left p-4 rounded-2xl transition-all duration-300 hover-lift ${isActive
                    ? 'bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500 text-white shadow-elegant-lg scale-[1.02]'
                    : 'bg-white/10 backdrop-blur-sm text-white border border-white/20 hover:bg-white/20 hover:border-white/40'
                    }`}
                >
                  <div className="flex items-start space-x-3">
                    <div
                      className={`flex-shrink-0 w-12 h-12 rounded-xl flex items-center justify-center transition-all ${isActive
                        ? 'bg-white/20 shadow-md'
                        : 'bg-white/10'
                        }`}
                    >
                      <svg
                        className={`w-6 h-6 ${isActive ? 'text-white' : 'text-white/80'}`}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                        />
                      </svg>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className={`font-bold mb-1.5 ${isActive ? 'text-white' : 'text-white'}`}>
                        {lecture.title}
                      </div>
                      <div className={`text-sm mb-2 ${isActive ? 'text-white/90' : 'text-white/70'}`}>
                        {lecture.session}
                      </div>
                      <div className="flex items-center space-x-2">
                        <svg
                          className={`w-4 h-4 ${isActive ? 'text-white/90' : 'text-white/60'}`}
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                        <span className={`text-xs font-medium ${isActive ? 'text-white/90' : 'text-white/60'}`}>
                          {lecture.duration}
                        </span>
                      </div>
                    </div>
                    {isActive && (
                      <div className="flex-shrink-0">
                        <div className="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center">
                          <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path
                              fillRule="evenodd"
                              d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                              clipRule="evenodd"
                            />
                          </svg>
                        </div>
                      </div>
                    )}
                  </div>
                </button>
              )
            })}
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-white/20 bg-white/5 backdrop-blur-sm">
            <div className="flex items-center space-x-2 text-sm text-white/80">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span className="font-medium">Select a lecture to view content</span>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default SidePanel

