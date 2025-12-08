import { useState, useEffect, useRef } from 'react'

interface TranscriptItem {
  time: string
  text: string
}

interface ContentTabsProps {
  activeTab: 'notes' | 'description' | 'transcript'
  onTabChange: (tab: 'notes' | 'description' | 'transcript') => void
  transcript: TranscriptItem[]
  description: string
  notes: string
  onTimestampClick?: (timeInSeconds: number) => void
  currentVideoTime?: number
}

const ContentTabs = ({ activeTab, onTabChange, transcript, description, notes, onTimestampClick, currentVideoTime = 0 }: ContentTabsProps) => {
  const [copied, setCopied] = useState(false)
  const transcriptRefs = useRef<(HTMLDivElement | null)[]>([])
  const transcriptContainerRef = useRef<HTMLDivElement>(null)

  const handleCopy = () => {
    const textToCopy = transcript.map(item => `${item.time}: ${item.text}`).join('\n\n')
    navigator.clipboard.writeText(textToCopy)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // Parse timestamp like "00:00 - 01:00" to seconds
  const parseTimestamp = (timeString: string): { start: number; end: number } => {
    const [startTime, endTime] = timeString.split(' - ')
    const [startMinutes, startSeconds] = (startTime || '0:0').split(':').map(Number)
    const [endMinutes, endSeconds] = (endTime || '0:0').split(':').map(Number)
    return {
      start: (startMinutes || 0) * 60 + (startSeconds || 0),
      end: (endMinutes || 0) * 60 + (endSeconds || 0)
    }
  }

  const handleTimestampClick = (timeString: string) => {
    if (onTimestampClick) {
      const { start } = parseTimestamp(timeString)
      onTimestampClick(start)
    }
  }

  // Find the active transcript item based on current video time
  const getActiveIndex = (): number => {
    for (let i = 0; i < transcript.length; i++) {
      const { start, end } = parseTimestamp(transcript[i].time)
      if (currentVideoTime >= start && currentVideoTime < end) {
        return i
      }
    }
    // If past the last item, return the last index
    if (transcript.length > 0) {
      const lastItem = parseTimestamp(transcript[transcript.length - 1].time)
      if (currentVideoTime >= lastItem.start) {
        return transcript.length - 1
      }
    }
    return -1
  }

  const activeIndex = getActiveIndex()

  // Auto-scroll to active item
  useEffect(() => {
    if (activeIndex >= 0 && activeTab === 'transcript' && transcriptRefs.current[activeIndex]) {
      const activeElement = transcriptRefs.current[activeIndex]
      if (activeElement && transcriptContainerRef.current) {
        const container = transcriptContainerRef.current
        const elementTop = activeElement.offsetTop
        const elementHeight = activeElement.offsetHeight
        const containerHeight = container.clientHeight
        const scrollTop = container.scrollTop

        // Check if element is not fully visible
        if (elementTop < scrollTop || elementTop + elementHeight > scrollTop + containerHeight) {
          // Scroll to center the active item
          container.scrollTo({
            top: elementTop - containerHeight / 2 + elementHeight / 2,
            behavior: 'smooth'
          })
        }
      }
    }
  }, [activeIndex, activeTab])

  return (
    <div className="w-full h-full flex flex-col bg-white/5 backdrop-blur-sm">
      {/* Tab Navigation */}
      <div className="flex border-b border-white/20 bg-gradient-to-r from-white/10 to-white/5 px-3 flex-shrink-0">
        <button
          onClick={() => onTabChange('notes')}
          className={`relative px-6 py-4 font-semibold text-sm transition-all duration-300 rounded-t-xl ${
            activeTab === 'notes'
              ? 'text-purple-600 bg-white/90 backdrop-blur-sm shadow-elegant'
              : 'text-white/70 hover:text-white hover:bg-white/10'
          }`}
        >
          <span className="flex items-center">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Notes
          </span>
          {activeTab === 'notes' && (
            <span className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 rounded-t-full"></span>
          )}
        </button>
        <button
          onClick={() => onTabChange('description')}
          className={`relative px-6 py-4 font-semibold text-sm transition-all duration-300 rounded-t-xl ${
            activeTab === 'description'
              ? 'text-purple-600 bg-white/90 backdrop-blur-sm shadow-elegant'
              : 'text-white/70 hover:text-white hover:bg-white/10'
          }`}
        >
          <span className="flex items-center">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Description
          </span>
          {activeTab === 'description' && (
            <span className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 rounded-t-full"></span>
          )}
        </button>
        <button
          onClick={() => onTabChange('transcript')}
          className={`relative px-6 py-4 font-semibold text-sm transition-all duration-300 rounded-t-xl ${
            activeTab === 'transcript'
              ? 'text-purple-600 bg-white/90 backdrop-blur-sm shadow-elegant'
              : 'text-white/70 hover:text-white hover:bg-white/10'
          }`}
        >
          <span className="flex items-center">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
            Transcript
          </span>
          {activeTab === 'transcript' && (
            <span className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-purple-500 via-pink-500 to-orange-500 rounded-t-full"></span>
          )}
        </button>
      </div>

      {/* Tab Content */}
      <div className="p-6 relative bg-white/90 backdrop-blur-sm flex-1 overflow-hidden flex flex-col">
        {activeTab === 'transcript' && (
          <>
            <button
              onClick={handleCopy}
              className="absolute top-8 right-8 p-3 text-gray-500 hover:text-purple-600 hover:bg-purple-50 rounded-xl transition-all duration-200 group hover-lift z-10"
              title="Copy transcript"
            >
              <svg
                className="w-5 h-5 group-hover:scale-110 transition-transform"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                />
              </svg>
            </button>
            {copied && (
              <div className="absolute top-8 right-24 bg-gradient-to-r from-green-500 to-emerald-500 text-white px-4 py-2 rounded-xl text-sm font-semibold shadow-elegant-lg animate-in fade-in slide-in-from-right z-10">
                ✓ Copied!
              </div>
            )}
            <div ref={transcriptContainerRef} className="flex-1 overflow-y-auto pr-4 scrollbar-custom">
              <div className="space-y-4">
                {transcript.map((item, index) => {
                  const isActive = index === activeIndex
                  return (
                    <div 
                      key={index}
                      ref={(el) => { transcriptRefs.current[index] = el }}
                      className={`group p-5 rounded-2xl transition-all duration-300 border-l-4 hover-lift ${
                        isActive
                          ? 'bg-gradient-to-r from-purple-50 via-pink-50 to-orange-50 border-purple-500 shadow-elegant scale-[1.01]'
                          : 'bg-white border-transparent hover:border-purple-300 hover:shadow-md'
                      }`}
                    >
                      <div className="flex items-center mb-3">
                        <div className={`text-xs font-bold px-4 py-1.5 rounded-full transition-all ${
                          isActive
                            ? 'text-white bg-gradient-to-r from-purple-500 to-pink-500 shadow-md'
                            : 'text-purple-600 bg-purple-100'
                        }`}>
                          {item.time}
                        </div>
                      </div>
                      <div 
                        onClick={() => handleTimestampClick(item.time)}
                        className={`leading-relaxed text-[15px] cursor-pointer transition-all duration-200 p-2 -m-2 rounded-lg ${
                          isActive
                            ? 'text-gray-900 font-semibold'
                            : 'text-gray-700 hover:text-purple-600 hover:bg-purple-50'
                        }`}
                        title="Click to jump to this time in video"
                      >
                        {item.text}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </>
        )}

        {activeTab === 'description' && (
          <div className="flex-1 overflow-y-auto scrollbar-custom">
            <div className="prose prose-slate max-w-none">
              <div className="p-8 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 rounded-2xl border-2 border-blue-200 shadow-elegant hover-lift">
                <div className="flex items-center space-x-2 mb-4">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-500 flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-bold text-gray-900">Lecture Description</h3>
                </div>
                <p className="text-gray-800 leading-relaxed text-[15px] whitespace-pre-line">
                  {description}
                </p>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'notes' && (
          <div className="flex-1 overflow-y-auto scrollbar-custom">
            <div className="p-8 bg-gradient-to-br from-purple-50 via-pink-50 to-orange-50 rounded-2xl border-2 border-purple-200 shadow-elegant hover-lift">
              <div className="flex items-center space-x-2 mb-6">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-gray-900">Lecture Notes</h3>
              </div>
              <div className="prose prose-slate max-w-none">
                <div className="text-gray-800 leading-relaxed text-[15px] whitespace-pre-line">
                  {notes.split('\n').map((line, index) => {
                    if (line.startsWith('-')) {
                      return (
                        <div key={index} className="flex items-start mb-4 group hover:bg-white/50 p-2 rounded-lg transition-colors">
                          <span className="text-purple-500 mr-3 mt-1 text-xl font-bold">•</span>
                          <span className="flex-1">{line.substring(1).trim()}</span>
                        </div>
                      )
                    }
                    if (line.trim() && !line.startsWith('-')) {
                      return (
                        <h3 key={index} className="font-bold text-gray-900 mb-4 mt-8 first:mt-0 text-xl border-b-2 border-purple-200 pb-2">
                          {line}
                        </h3>
                      )
                    }
                    return <br key={index} />
                  })}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ContentTabs

