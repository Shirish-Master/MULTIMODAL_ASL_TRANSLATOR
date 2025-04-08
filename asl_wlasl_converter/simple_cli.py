#!/usr/bin/env python3
"""
Simple CLI for ASL WLASL Converter

A basic command-line version that doesn't rely on moviepy.
This script allows you to look up individual ASL videos for words.
"""

import os
import sys
import json
import argparse
import shutil
import random

# Constants
DEFAULT_JSON_PATH = os.path.join(os.path.dirname(__file__), 'data', 'WLASL_v0.3.json')
DEFAULT_VIDEOS_DIR = os.path.join(os.path.dirname(__file__), 'data', 'videos')
# Try archive-3/videos if data/videos doesn't exist
if not os.path.exists(DEFAULT_VIDEOS_DIR):
    archive3_videos_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'archive-3', 'videos')
    if os.path.exists(archive3_videos_path):
        DEFAULT_VIDEOS_DIR = archive3_videos_path


def load_wlasl_json(json_path=DEFAULT_JSON_PATH):
    """Load and parse the WLASL JSON file."""
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading WLASL JSON: {e}")
        return None


def text_to_gloss(text):
    """Simple text to gloss conversion."""
    # Simple text preprocessing
    text = text.lower()
    
    # Remove punctuation and split into words
    words = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in text).split()
    
    # Filter out common words that might not be needed in ASL
    skip_words = {'a', 'an', 'the', 'is', 'are', 'am', 'was', 'were', 'be', 'been', 'being'}
    
    filtered_words = []
    for word in words:
        if word not in skip_words:
            filtered_words.append(word)
    
    return filtered_words


def get_video_for_word(word, json_path=DEFAULT_JSON_PATH, videos_dir=DEFAULT_VIDEOS_DIR):
    """Get a video file path for a given word."""
    data = load_wlasl_json(json_path)
    if not data:
        return None
    
    word = word.lower()
    for entry in data:
        if entry['gloss'].lower() == word and 'instances' in entry and entry['instances']:
            for instance in entry['instances']:
                video_filename = None
                if 'video_id' in instance:
                    video_filename = f"{instance['video_id']}.mp4"
                elif 'instance_id' in instance:
                    video_filename = f"{instance['instance_id']:05d}.mp4"
                    
                if video_filename:
                    video_path = os.path.join(videos_dir, video_filename)
                    if os.path.exists(video_path):
                        return video_path
    return None


def get_random_word(json_path=DEFAULT_JSON_PATH):
    """Get a random word from the dataset."""
    data = load_wlasl_json(json_path)
    if not data:
        return None
    
    # Get all available words
    words = [entry['gloss'].lower() for entry in data]
    if not words:
        return None
    
    return random.choice(words)


def word_lookup_command(args):
    """Handle the word-lookup command."""
    video_path = get_video_for_word(args.word, args.json, args.videos)
    
    if not video_path:
        print(f"Error: No video found for word '{args.word}'")
        return
    
    print(f"Found video for word '{args.word}': {video_path}")
    
    if args.output:
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        shutil.copy(video_path, args.output)
        print(f"Copied video to: {args.output}")


def random_word_command(args):
    """Handle the random-word command."""
    word = get_random_word(args.json)
    
    if not word:
        print("Error: Could not get a random word from the dataset")
        return
    
    print(f"Random word: {word}")
    
    video_path = get_video_for_word(word, args.json, args.videos)
    
    if not video_path:
        print(f"Error: No video found for word '{word}'")
        return
    
    print(f"Found video: {video_path}")
    
    if args.output:
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        shutil.copy(video_path, args.output)
        print(f"Copied video to: {args.output}")


def list_words_command(args):
    """Handle the list-words command."""
    data = load_wlasl_json(args.json)
    if not data:
        print("Error: Could not load WLASL JSON")
        return
    
    words = [entry['gloss'].lower() for entry in data]
    if not words:
        print("No words found in the dataset")
        return
    
    print(f"Found {len(words)} words in the dataset:")
    
    if args.limit:
        words = words[:args.limit]
    
    # Print words in columns
    col_width = max(len(word) for word in words) + 2
    num_cols = 5
    for i in range(0, len(words), num_cols):
        row = words[i:i+num_cols]
        print("".join(word.ljust(col_width) for word in row))


def sentence_lookup_command(args):
    """Handle the sentence-lookup command."""
    words = text_to_gloss(args.text)
    
    if not words:
        print("Error: No words to look up after filtering")
        return
    
    print(f"Glossed text: {' '.join(words)}")
    
    # Find videos for each word
    videos = []
    missing = []
    
    for word in words:
        video_path = get_video_for_word(word, args.json, args.videos)
        if video_path:
            videos.append((word, video_path))
        else:
            missing.append(word)
    
    # Print results
    if videos:
        print("\nFound videos for the following words:")
        for word, path in videos:
            print(f"  {word}: {path}")
    
    if missing:
        print("\nNo videos found for the following words:")
        for word in missing:
            print(f"  {word}")
    
    print(f"\nTotal: {len(videos)} videos found, {len(missing)} missing")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Simple ASL WLASL Converter CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Word lookup command
    word_lookup_parser = subparsers.add_parser("word-lookup", help="Look up a video for a word")
    word_lookup_parser.add_argument("word", help="Word to look up")
    word_lookup_parser.add_argument("--json", default=DEFAULT_JSON_PATH, help="Path to WLASL JSON file")
    word_lookup_parser.add_argument("--videos", default=DEFAULT_VIDEOS_DIR, help="Path to videos directory")
    word_lookup_parser.add_argument("--output", help="Output path to copy the video")
    
    # Random word command
    random_word_parser = subparsers.add_parser("random-word", help="Get a random word and its video")
    random_word_parser.add_argument("--json", default=DEFAULT_JSON_PATH, help="Path to WLASL JSON file")
    random_word_parser.add_argument("--videos", default=DEFAULT_VIDEOS_DIR, help="Path to videos directory")
    random_word_parser.add_argument("--output", help="Output path to copy the video")
    
    # List words command
    list_words_parser = subparsers.add_parser("list-words", help="List available words in the dataset")
    list_words_parser.add_argument("--json", default=DEFAULT_JSON_PATH, help="Path to WLASL JSON file")
    list_words_parser.add_argument("--limit", type=int, help="Limit the number of words to display")
    
    # Sentence lookup command
    sentence_lookup_parser = subparsers.add_parser("sentence-lookup", help="Look up videos for words in a sentence")
    sentence_lookup_parser.add_argument("text", help="Text to convert to gloss and look up")
    sentence_lookup_parser.add_argument("--json", default=DEFAULT_JSON_PATH, help="Path to WLASL JSON file")
    sentence_lookup_parser.add_argument("--videos", default=DEFAULT_VIDEOS_DIR, help="Path to videos directory")
    
    args = parser.parse_args()
    
    if args.command == "word-lookup":
        word_lookup_command(args)
    elif args.command == "random-word":
        random_word_command(args)
    elif args.command == "list-words":
        list_words_command(args)
    elif args.command == "sentence-lookup":
        sentence_lookup_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()