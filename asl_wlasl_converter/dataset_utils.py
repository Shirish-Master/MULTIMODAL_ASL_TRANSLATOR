"""
WLASL Dataset Utilities

This module provides functions for working with the WLASL dataset:
- Loading the WLASL JSON metadata
- Finding videos for given words
- Creating mappings between signs and videos
"""

import os
import json
import random
from typing import Dict, List, Tuple, Optional, Union


class WLASLDataset:
    """A class to handle the WLASL dataset."""
    
    def __init__(self, json_path: str, videos_dir: str):
        """
        Initialize the WLASL dataset handler.
        
        Args:
            json_path: Path to the WLASL JSON file (e.g., WLASL_v0.3.json)
            videos_dir: Directory containing the video files
        """
        self.json_path = json_path
        self.videos_dir = videos_dir
        self.data = self._load_json()
        self.gloss_to_videos = self._build_gloss_to_videos_mapping()
        self.id_to_gloss = self._build_id_to_gloss_mapping()
        self.gloss_to_id = {v: k for k, v in self.id_to_gloss.items()}
        
    def _load_json(self) -> List[Dict]:
        """Load the WLASL JSON file."""
        with open(self.json_path, 'r') as f:
            return json.load(f)
    
    def _build_gloss_to_videos_mapping(self) -> Dict[str, List[str]]:
        """Build a mapping from gloss (word) to list of video filenames."""
        gloss_to_videos = {}
        
        for entry in self.data:
            gloss = entry['gloss'].lower()
            videos = []
            
            for instance in entry['instances']:
                # Extract the video filename from the last part of the URL or the instance_id
                if 'video_id' in instance:
                    video_filename = f"{instance['video_id']}.mp4"
                else:
                    # Use instance_id if video_id is not present
                    video_filename = f"{instance['instance_id']:05d}.mp4"
                
                # Check if the video file exists
                video_path = os.path.join(self.videos_dir, video_filename)
                if os.path.exists(video_path):
                    videos.append(video_filename)
            
            if videos:  # Only add entry if there are valid videos
                gloss_to_videos[gloss] = videos
        
        return gloss_to_videos
    
    def _build_id_to_gloss_mapping(self) -> Dict[int, str]:
        """Build a mapping from ID to gloss (word)."""
        id_to_gloss = {}
        
        for i, entry in enumerate(self.data):
            id_to_gloss[i] = entry['gloss'].lower()
        
        return id_to_gloss
    
    def get_video_for_word(self, word: str) -> Optional[str]:
        """
        Get a random video filename for a given word.
        
        Args:
            word: The word/gloss to find a video for
            
        Returns:
            A video filename if available, None otherwise
        """
        word = word.lower()
        if word in self.gloss_to_videos and self.gloss_to_videos[word]:
            return random.choice(self.gloss_to_videos[word])
        return None
    
    def get_specific_video(self, word: str, index: int = 0) -> Optional[str]:
        """
        Get a specific video for a word by index.
        
        Args:
            word: The word/gloss to find a video for
            index: The index of the video to retrieve (default: 0)
            
        Returns:
            A video filename if available, None otherwise
        """
        word = word.lower()
        if word in self.gloss_to_videos and len(self.gloss_to_videos[word]) > index:
            return self.gloss_to_videos[word][index]
        return None
    
    def get_video_path(self, video_filename: str) -> str:
        """
        Get the full path for a video filename.
        
        Args:
            video_filename: The filename of the video
            
        Returns:
            The full path to the video
        """
        return os.path.join(self.videos_dir, video_filename)
    
    def get_available_words(self) -> List[str]:
        """
        Get a list of all available words that have videos.
        
        Returns:
            List of available words
        """
        return list(self.gloss_to_videos.keys())
    
    def get_random_word(self) -> str:
        """
        Get a random word from the available words.
        
        Returns:
            A random word
        """
        return random.choice(list(self.gloss_to_videos.keys()))
    
    def get_random_video(self) -> Tuple[str, str]:
        """
        Get a random video from the dataset.
        
        Returns:
            A tuple of (word, video_filename)
        """
        word = self.get_random_word()
        video = self.get_video_for_word(word)
        return word, video


def text_to_gloss(text: str) -> List[str]:
    """
    Convert English text to a simplified ASL gloss.
    This is a basic implementation and doesn't account for ASL grammar rules.
    
    Args:
        text: English text
        
    Returns:
        List of words in simplified ASL gloss order
    """
    # Simple text preprocessing
    text = text.lower()
    
    # Remove punctuation and split into words
    words = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in text).split()
    
    # Filter out common words that might not be needed in ASL
    # This is a basic approach - real ASL glossing is more complex
    filtered_words = []
    skip_words = {'a', 'an', 'the', 'is', 'are', 'am', 'was', 'were', 'be', 'been', 'being'}
    
    for word in words:
        if word not in skip_words:
            filtered_words.append(word)
    
    return filtered_words


if __name__ == "__main__":
    # Example usage
    json_path = "/path/to/WLASL_v0.3.json"
    videos_dir = "/path/to/videos"
    
    if os.path.exists(json_path) and os.path.exists(videos_dir):
        dataset = WLASLDataset(json_path, videos_dir)
        print(f"Available words: {len(dataset.get_available_words())}")
        
        word = "book"
        video = dataset.get_video_for_word(word)
        if video:
            print(f"Video for '{word}': {video}")
        else:
            print(f"No video found for '{word}'")
            
        # Example text to gloss
        text = "I want to learn sign language"
        gloss = text_to_gloss(text)
        print(f"Text: '{text}'")
        print(f"Gloss: {gloss}")
    else:
        print("Please set the correct paths to the WLASL JSON and videos directory.")