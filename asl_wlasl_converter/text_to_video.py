"""
Text to ASL Video Converter

This script converts English text to ASL videos by:
1. Converting text to ASL gloss
2. Detecting and resolving homonyms based on context
3. Finding corresponding videos for each word in the gloss
4. Stitching those videos together to create a continuous ASL video
"""

import os
import argparse
import tempfile
import json
from typing import List, Dict, Optional, Tuple
import cv2

# Import directly from moviepy
import moviepy
from moviepy import VideoFileClip, concatenate_videoclips

from dataset_utils import WLASLDataset, text_to_gloss


def detect_homonyms(text: str, words: List[str]) -> Dict[str, str]:
    """
    Detect homonyms in a sentence and determine their meaning.
    
    Args:
        text: The full original text
        words: List of individual words to check for homonyms
        
    Returns:
        Dictionary mapping homonym words to their contextual meaning
    """
    homonym_meanings = {}
    # Get API key from environment variable
    openai_api_key = os.environ.get("OPENAI_API_KEY", "")
    
    if not openai_api_key:
        print("Warning: No OpenAI API key found. Homonym detection will be skipped.")
        return homonym_meanings
        
    try:
        import requests
        
        # Common homonyms to check for (extend as needed)
        common_homonyms = [
            "bat", "bank", "bark", "bear", "bow", "fair", "kind", 
            "letter", "light", "mean", "might", "present", "ring", 
            "rock", "rose", "saw", "seal", "spring", "star", "tie"
        ]
        
        # Check if any of the words in the text are homonyms
        potential_homonyms = [word for word in words if word.lower() in common_homonyms]
        
        if not potential_homonyms:
            return homonym_meanings
            
        print(f"Potential homonyms detected: {potential_homonyms}")
        
        # If homonyms are detected, use OpenAI API to determine their meaning
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a homonym detection assistant."},
                {"role": "user", "content": f"Analyze this sentence: '{text}'. Identify any homonyms and return their meaning in JSON format. For example: {{\"bat\": \"animal\"}}. Only include words that are homonyms in this specific context."}
            ]
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Try to extract JSON from the response
            try:
                # Find JSON in the response
                import re
                json_match = re.search(r'{.*}', content, re.DOTALL)
                if json_match:
                    meanings = json.loads(json_match.group(0))
                    homonym_meanings = meanings
                    print(f"Homonym meanings detected: {homonym_meanings}")
                else:
                    print("No homonym meanings found in API response")
            except json.JSONDecodeError:
                print(f"Failed to parse homonym meanings from API response: {content}")
        else:
            print(f"API request failed with status code {response.status_code}")
            
    except Exception as e:
        print(f"Error in homonym detection: {e}")
        
    return homonym_meanings


def create_asl_video_from_text(
    text: str, 
    dataset: WLASLDataset, 
    output_path: str,
    include_transitions: bool = True,
    resize_videos: bool = True,
    target_size: tuple = (640, 480),
    detect_homonyms_enabled: bool = True
) -> Optional[str]:
    """
    Create an ASL video from English text.
    
    Args:
        text: English text to convert to ASL
        dataset: WLASL dataset object
        output_path: Path to save the output video
        include_transitions: Whether to include fade transitions between clips
        resize_videos: Whether to resize all videos to the same dimensions
        target_size: Target video dimensions (width, height)
        detect_homonyms_enabled: Whether to detect and resolve homonyms
        
    Returns:
        Path to the output video if successful, None otherwise
    """
    # Convert text to gloss
    gloss = text_to_gloss(text)
    print(f"Glossed text: {gloss}")
    
    # Detect homonyms if enabled
    homonym_meanings = {}
    if detect_homonyms_enabled:
        homonym_meanings = detect_homonyms(text, gloss)
        if homonym_meanings:
            print(f"Detected homonyms with meanings: {homonym_meanings}")
    
    # Store homonym meanings for return
    result_homonyms = homonym_meanings
    
    # Find videos for each word in the gloss
    video_paths = []
    missing_words = []
    
    for word in gloss:
        # Check if word is a homonym with specific meaning
        specific_meaning = homonym_meanings.get(word.lower())
        
        if specific_meaning:
            print(f"Word '{word}' is a homonym meaning '{specific_meaning}'")
            # Here you would ideally look up the specific meaning video
            # This would require extending the dataset to map meanings to specific videos
            
            # For now, we'll just use the regular video but log the meaning
            video_filename = dataset.get_video_for_word(word)
            if video_filename:
                video_path = dataset.get_video_path(video_filename)
                video_paths.append(video_path)
                print(f"Found video for '{word}' (meaning: {specific_meaning}): {video_filename}")
            else:
                missing_words.append(f"{word} ({specific_meaning})")
                print(f"No video found for '{word}' with meaning '{specific_meaning}'")
        else:
            # Regular word processing (non-homonym)
            video_filename = dataset.get_video_for_word(word)
            if video_filename:
                video_path = dataset.get_video_path(video_filename)
                video_paths.append(video_path)
                print(f"Found video for '{word}': {video_filename}")
            else:
                missing_words.append(word)
                print(f"No video found for '{word}'")
    
    if missing_words:
        print(f"Warning: No videos found for words: {missing_words}")
    
    if not video_paths:
        print("Error: No videos found for any words in the input text")
        return None, {}
    
    # Stitch videos together
    print("Stitching videos together...")
    clips = []
    
    try:
        for path in video_paths:
            clip = VideoFileClip(path)
            
            # Resize if needed
            if resize_videos:
                clip = clip.resize(target_size)
            
            clips.append(clip)
        
        # Add transitions if required
        if include_transitions and len(clips) > 1:
            final_clip = concatenate_videoclips(clips, method="compose")
        else:
            final_clip = concatenate_videoclips(clips, method="chain")
        
        # Write the final video
        final_clip.write_videofile(output_path, codec="libx264", audio=False)
        print(f"ASL video created: {output_path}")
        
        # Clean up
        for clip in clips:
            clip.close()
        final_clip.close()
        
        return output_path, result_homonyms
        
    except Exception as e:
        print(f"Error stitching videos: {e}")
        
        # Clean up any open clips
        for clip in clips:
            try:
                clip.close()
            except:
                pass
                
        return None, {}


def main():
    """Main function to run the text-to-video converter from command line."""
    parser = argparse.ArgumentParser(description="Convert English text to ASL video")
    parser.add_argument("--text", type=str, required=True, help="English text to convert to ASL")
    parser.add_argument("--json", type=str, required=True, help="Path to WLASL JSON file")
    parser.add_argument("--videos", type=str, required=True, help="Path to WLASL videos directory")
    parser.add_argument("--output", type=str, required=True, help="Output video path")
    parser.add_argument("--no-transitions", action="store_true", help="Disable fade transitions")
    parser.add_argument("--no-resize", action="store_true", help="Disable video resizing")
    parser.add_argument("--no-homonym-detection", action="store_true", help="Disable homonym detection")
    parser.add_argument("--api-key", type=str, help="OpenAI API key for homonym detection")
    
    args = parser.parse_args()
    
    # Check if paths exist
    if not os.path.exists(args.json):
        print(f"Error: JSON file not found: {args.json}")
        return
        
    if not os.path.exists(args.videos):
        print(f"Error: Videos directory not found: {args.videos}")
        return
    
    # Set API key if provided
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key
        
    # Create dataset
    dataset = WLASLDataset(args.json, args.videos)
    
    # Create ASL video
    create_asl_video_from_text(
        args.text,
        dataset,
        args.output,
        include_transitions=not args.no_transitions,
        resize_videos=not args.no_resize,
        detect_homonyms_enabled=not args.no_homonym_detection
    )


if __name__ == "__main__":
    main()