// Lecture data types and loader
// This file loads lecture data from the generated JSON file

export interface TranscriptItem {
  time: string
  text: string
}

export interface Lecture {
  id: string
  title: string
  session: string
  description: string
  duration: string
  videoUrl: string
  transcript: TranscriptItem[]
  notes: string
}

let lecturesCache: Lecture[] | null = null

/**
 * Load lectures from the generated JSON file
 */
export async function loadLectures(): Promise<Lecture[]> {
  if (lecturesCache) {
    return lecturesCache
  }

  try {
    const response = await fetch('/data/lectures.json')
    if (!response.ok) {
      throw new Error(`Failed to load lectures: ${response.statusText}`)
    }

    const data: Lecture[] = await response.json()
    lecturesCache = data
    return data
  } catch (error) {
    console.error('Error loading lectures:', error)
    // Return empty array as fallback
    return []
  }
}

/**
 * Get a specific lecture by ID
 */
export function getLectureById(lectures: Lecture[], id: string): Lecture | undefined {
  return lectures.find(lecture => lecture.id === id)
}

/**
 * Clear the cache (useful for development/testing)
 */
export function clearLecturesCache() {
  lecturesCache = null
}
