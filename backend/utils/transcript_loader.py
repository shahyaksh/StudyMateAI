"""
Utility functions for loading and parsing transcript data.
"""

import os
import re
from typing import List, Dict, Optional, Tuple

def parse_timestamp(time_str: str) -> Tuple[int, int]:
    """
    Parse timestamp string like '00:00 - 01:00' to (start_seconds, end_seconds).
    
    Args:
        time_str: Timestamp string in format 'MM:SS - MM:SS'
        
    Returns:
        Tuple of (start_seconds, end_seconds)
    """
    try:
        start, end = time_str.split(' - ')
        
        def to_seconds(time):
            parts = time.strip().split(':')
            if len(parts) == 2:
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            return 0
        
        return (to_seconds(start), to_seconds(end))
    except:
        return (0, 0)

def load_transcript(lecture_id: str) -> List[Dict[str, str]]:
    """
    Load transcript for a specific lecture.
    
    Args:
        lecture_id: Lecture identifier (e.g., 'lecture-7', 'lecture-10')
        
    Returns:
        List of transcript segments with 'time' and 'text' keys
    """
    # Convert lecture-7 to transcript_lecture_7.txt
    filename = f"transcript_{lecture_id.replace('-', '_')}.txt"
    
    # Get the data directory path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', 'data')
    transcript_path = os.path.join(data_dir, filename)
    
    if not os.path.exists(transcript_path):
        print(f"Warning: Transcript file not found: {transcript_path}")
        return []
    
    transcript = []
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Parse line format: "MM:SS - MM:SS: text"
                match = re.match(r'([\d:]+\s*-\s*[\d:]+):\s*(.+)', line)
                if match:
                    time_range = match.group(1)
                    text = match.group(2)
                    transcript.append({
                        'time': time_range,
                        'text': text
                    })
        
        print(f"✓ Loaded {len(transcript)} transcript segments for {lecture_id}")
        return transcript
    except Exception as e:
        print(f"Error loading transcript for {lecture_id}: {e}")
        return []

def get_transcript_context(
    lecture_id: str,
    timestamp: float,
    num_segments: int = 3
) -> str:
    """
    Get transcript context around a specific timestamp.
    Returns the PREVIOUS (num_segments - 1) segments and the current segment.
    
    Args:
        lecture_id: Lecture identifier
        timestamp: Current timestamp in seconds
        num_segments: Number of segments to return (default: 3 for previous 2 + current)
        
    Returns:
        Formatted string with transcript segments
    """
    transcript = load_transcript(lecture_id)
    
    if not transcript:
        return "No transcript available."
    
    # Find the segment containing the current timestamp
    current_index = None
    for i, segment in enumerate(transcript):
        start_time, end_time = parse_timestamp(segment['time'])
        if start_time <= timestamp < end_time:
            current_index = i
            break
    
    # If timestamp is beyond all segments, use the last segment
    if current_index is None:
        if timestamp >= parse_timestamp(transcript[-1]['time'])[1]:
            current_index = len(transcript) - 1
        else:
            # Timestamp before first segment, use first segment
            current_index = 0
    
    # Get previous (num_segments - 1) segments + current segment
    start_index = max(0, current_index - (num_segments - 1))
    segments_to_include = []
    
    for i in range(start_index, current_index + 1):
        segments_to_include.append(transcript[i])
    
    # Format the segments
    formatted_segments = []
    for i, segment in enumerate(segments_to_include):
        if i == len(segments_to_include) - 1:
            # Last segment is the current one
            formatted_segments.append(f"[CURRENT at {segment['time']}]: {segment['text']}")
        else:
            # Calculate how many segments back
            segments_back = len(segments_to_include) - 1 - i
            formatted_segments.append(f"[PREVIOUS {segments_back} at {segment['time']}]: {segment['text']}")
    
    return "\n\n".join(formatted_segments)

def get_all_transcript_text(lecture_id: str) -> str:
    """
    Get all transcript text for a lecture as a single string.
    
    Args:
        lecture_id: Lecture identifier
        
    Returns:
        Full transcript text
    """
    transcript = load_transcript(lecture_id)
    
    if not transcript:
        return "No transcript available."
    
    return "\n\n".join([
        f"[{seg['time']}] {seg['text']}"
        for seg in transcript
    ])
