import { useRef, useEffect, useImperativeHandle, forwardRef } from 'react'

interface VideoPlayerProps {
  videoUrl: string
  onTimeUpdate?: (currentTime: number) => void
}

export interface VideoPlayerRef {
  seekTo: (timeInSeconds: number) => void
}

const VideoPlayer = forwardRef<VideoPlayerRef, VideoPlayerProps>(({ videoUrl, onTimeUpdate }, ref) => {
  const videoRef = useRef<HTMLVideoElement>(null)

  useImperativeHandle(ref, () => ({
    seekTo: (timeInSeconds: number) => {
      if (videoRef.current) {
        videoRef.current.currentTime = timeInSeconds
        videoRef.current.play()
      }
    }
  }))

  useEffect(() => {
    const video = videoRef.current
    if (!video || !onTimeUpdate) return

    const handleTimeUpdate = () => {
      onTimeUpdate(video.currentTime)
    }

    video.addEventListener('timeupdate', handleTimeUpdate)
    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate)
    }
  }, [onTimeUpdate])

  return (
    <div className="relative w-full h-full bg-gradient-to-br from-gray-900 via-purple-900 to-black group">
      <video
        ref={videoRef}
        src={videoUrl}
        controls
        className="w-full h-full object-contain"
        controlsList="nodownload"
      >
        Your browser does not support the video tag.
      </video>
      <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
      <div className="absolute top-4 left-4 bg-black/50 backdrop-blur-sm px-3 py-1.5 rounded-lg border border-white/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <span className="text-white text-xs font-semibold">Lecture Video</span>
      </div>
    </div>
  )
})

VideoPlayer.displayName = 'VideoPlayer'

export default VideoPlayer

