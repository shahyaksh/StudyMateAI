#!/usr/bin/env python3
"""
Enhanced preprocessing script to convert raw transcripts to:
1. Formatted text files with timestamps
2. JSON file for frontend consumption
"""

import os
import re
import json
from typing import List, Tuple, Dict, Any
from pathlib import Path

def format_time(seconds: int) -> str:
    """Convert seconds to MM:SS format."""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"

def estimate_reading_time(text: str, words_per_minute: int = 40) -> int:
    """Estimate reading time in seconds based on word count."""
    words = len(text.split())
    minutes = words / words_per_minute
    return int(minutes * 60)

def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    sentences = re.split(r'([.!?]\s+)', text)
    result = []
    for i in range(0, len(sentences) - 1, 2):
        if i + 1 < len(sentences):
            result.append(sentences[i] + sentences[i + 1])
        else:
            result.append(sentences[i])
    if len(sentences) % 2 == 1:
        result.append(sentences[-1])
    return [s.strip() for s in result if s.strip()]

def split_into_time_segments(text: str, segment_duration: int = 60) -> List[Tuple[str, int, int]]:
    """
    Split text into segments with exactly segment_duration seconds each.
    
    Args:
        text: The full transcript text
        segment_duration: Target duration for each segment in seconds (default: 60)
    
    Returns:
        List of tuples: (segment_text, start_time, end_time)
    """
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    all_sentences = []
    for para in paragraphs:
        sentences = split_into_sentences(para)
        all_sentences.extend(sentences)
    
    segments = []
    current_segment = []
    current_time = 0
    segment_start_time = 0
    
    for sentence in all_sentences:
        sentence_time = estimate_reading_time(sentence)
        
        if current_segment and current_time + sentence_time > segment_duration:
            segment_text = ' '.join(current_segment)
            segments.append((segment_text, segment_start_time, segment_start_time + segment_duration))
            
            current_segment = [sentence]
            segment_start_time += segment_duration
            current_time = sentence_time
        else:
            current_segment.append(sentence)
            current_time += sentence_time
    
    if current_segment:
        segment_text = ' '.join(current_segment)
        actual_duration = estimate_reading_time(segment_text)
        if actual_duration <= segment_duration * 1.2:
            segments.append((segment_text, segment_start_time, segment_start_time + segment_duration))
        else:
            remaining_text = segment_text
            start = segment_start_time
            while remaining_text:
                words = remaining_text.split()
                target_words = int(segment_duration * 150 / 60)
                
                if len(words) <= target_words:
                    segments.append((remaining_text, start, start + segment_duration))
                    break    
                else:
                    sentences = split_into_sentences(remaining_text)
                    segment_sentences = []
                    segment_words = 0
                    
                    for sent in sentences:
                        sent_words = len(sent.split())
                        if segment_words + sent_words <= target_words:
                            segment_sentences.append(sent)
                            segment_words += sent_words
                        else:
                            break
                    
                    if segment_sentences:
                        segment_text_part = ' '.join(segment_sentences)
                        segments.append((segment_text_part, start, start + segment_duration))
                        start += segment_duration
                        remaining_text = ' '.join(sentences[len(segment_sentences):])
                    else:
                        segments.append((sentences[0], start, start + segment_duration))
                        start += segment_duration
                        remaining_text = ' '.join(sentences[1:])
    
    return segments

def format_transcript_with_timestamps(segments: List[Tuple[str, int, int]]) -> str:
    """Format segments into transcript format with timestamps."""
    formatted_lines = []
    
    for segment_text, start_time, end_time in segments:
        start_str = format_time(start_time)
        end_str = format_time(end_time)
        formatted_lines.append(f"{start_str} - {end_str}: {segment_text}")
    
    return '\n'.join(formatted_lines)

def extract_description(text: str, max_length: int = 300) -> str:
    """Extract a description from the first paragraph of the transcript."""
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    if paragraphs:
        first_para = paragraphs[0]
        if len(first_para) > max_length:
            return first_para[:max_length] + '...'
        return first_para
    return "No description available."

def extract_notes(segments: List[Tuple[str, int, int]]) -> str:
    """Generate notes from the transcript segments."""
    # For now, just create a simple summary
    # In a real implementation, you might use NLP to extract key points
    notes = "Key Topics Covered:\n"
    notes += f"- Total segments: {len(segments)}\n"
    notes += f"- Duration: {format_time(segments[-1][2])}\n"
    notes += "- Detailed transcript available in segments"
    return notes

def create_lecture_json(
    lecture_id: str,
    lecture_number: int,
    title: str,
    raw_text: str,
    segments: List[Tuple[str, int, int]],
    video_url: str
) -> Dict[str, Any]:
    """Create a JSON structure for a lecture."""
    
    # Convert segments to transcript items
    transcript_items = []
    for segment_text, start_time, end_time in segments:
        transcript_items.append({
            "time": f"{format_time(start_time)} - {format_time(end_time)}",
            "text": segment_text
        })
    
    # Extract description and notes
    description = extract_description(raw_text)
    notes = extract_notes(segments)
    
    # Calculate duration
    total_duration = segments[-1][2] if segments else 0
    duration_str = f"{total_duration // 60} min"
    
    return {
        "id": lecture_id,
        "title": title,
        "session": f"Session {lecture_number}",
        "description": description,
        "duration": duration_str,
        "videoUrl": video_url,
        "transcript": transcript_items,
        "notes": notes
    }

def preprocess_transcript(
    input_path: str,
    output_txt_path: str,
    segment_duration: int = 60
) -> List[Tuple[str, int, int]]:
    """
    Preprocess raw transcript file and save formatted version.
    
    Returns:
        List of segments for JSON generation
    """
    print(f"Reading raw transcript from: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    
    print(f"Raw transcript length: {len(raw_text)} characters")
    
    print(f"Splitting into segments (target duration: {segment_duration} seconds)...")
    segments = split_into_time_segments(raw_text, segment_duration)
    print(f"Created {len(segments)} segments")
    
    formatted_transcript = format_transcript_with_timestamps(segments)
    
    print(f"Writing formatted transcript to: {output_txt_path}")
    with open(output_txt_path, 'w', encoding='utf-8') as f:
        f.write(formatted_transcript)
    
    print(f"✓ Successfully processed transcript!")
    print(f"  Total segments: {len(segments)}")
    print(f"  Estimated total duration: {format_time(segments[-1][2])}")
    
    return segments, raw_text

# Lecture metadata configuration
LECTURE_CONFIG = {
    "lecture-7": {
        "number": 7,
        "title": "Introduction to Large Language Models",
        "video_url": "/video/Lecture-7.mp4"
    },
    "lecture-10": {
        "number": 10,
        "title": "Fine-Tuning Large Language Models",
        "video_url": "/video/Lecture-10.mp4"
    }
}

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')
    raw_data_dir = os.path.join(data_dir, 'raw_data')
    
    # Output directory for frontend JSON
    frontend_data_dir = os.path.join(script_dir, '..', 'public', 'data')
    os.makedirs(frontend_data_dir, exist_ok=True)
    
    if not os.path.exists(raw_data_dir):
        print(f"Error: Raw data directory not found at {raw_data_dir}")
        exit(1)
    
    # Find all transcript files
    transcript_files = []
    for filename in os.listdir(raw_data_dir):
        file_path = os.path.join(raw_data_dir, filename)
        if os.path.isfile(file_path) and filename.startswith('lecture'):
            transcript_files.append((filename, file_path))
    
    if not transcript_files:
        print(f"Error: No transcript files found in {raw_data_dir}")
        exit(1)
    
    print("="*60)
    print("TRANSCRIPT PREPROCESSING")
    print("="*60)
    print(f"Found {len(transcript_files)} transcript files:")
    for filename, _ in transcript_files:
        print(f"  - {filename}")
    print("="*60 + "\n")
    
    os.makedirs(data_dir, exist_ok=True)
    
    # Store all lectures for JSON output
    all_lectures = []
    
    # Process each transcript file
    for filename, input_path in transcript_files:
        print("\n" + "-"*60)
        print(f"Processing: {filename}")
        print("-"*60)
        
        # Extract lecture ID (e.g., "lecture-10" from "lecture-10")
        lecture_id = filename.replace('.txt', '')
        
        # Create output filename for text format
        output_filename = f"transcript_{filename.replace('-', '_')}.txt"
        output_path = os.path.join(data_dir, output_filename)
        
        try:
            # Process the transcript
            segments, raw_text = preprocess_transcript(
                input_path=input_path,
                output_txt_path=output_path,
                segment_duration=60
            )
            print(f"✅ Saved text format to: {output_filename}")
            
            # Get lecture metadata
            if lecture_id in LECTURE_CONFIG:
                config = LECTURE_CONFIG[lecture_id]
                lecture_json = create_lecture_json(
                    lecture_id=lecture_id,
                    lecture_number=config["number"],
                    title=config["title"],
                    raw_text=raw_text,
                    segments=segments,
                    video_url=config["video_url"]
                )
                all_lectures.append(lecture_json)
                print(f"✅ Added to JSON output: {config['title']}")
            else:
                print(f"⚠️  No metadata found for {lecture_id}, skipping JSON generation")
                
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Write combined JSON file for frontend
    if all_lectures:
        json_output_path = os.path.join(frontend_data_dir, 'lectures.json')
        print("\n" + "="*60)
        print("GENERATING JSON FOR FRONTEND")
        print("="*60)
        
        with open(json_output_path, 'w', encoding='utf-8') as f:
            json.dump(all_lectures, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved lectures JSON to: {json_output_path}")
        print(f"   Total lectures: {len(all_lectures)}")
        for lecture in all_lectures:
            print(f"   - {lecture['id']}: {lecture['title']}")
    
    print("\n" + "="*60)
    print("✅ ALL TRANSCRIPTS PROCESSED!")
    print("="*60)
    print(f"\nText files saved in: {data_dir}")
    print(f"JSON file saved in: {frontend_data_dir}")
    print("\nOutput files:")
    for filename, _ in transcript_files:
        output_filename = f"transcript_{filename.replace('-', '_')}.txt"
        print(f"  - {output_filename}")
    if all_lectures:
        print(f"  - lectures.json (for frontend)")
    print("="*60 + "\n")
