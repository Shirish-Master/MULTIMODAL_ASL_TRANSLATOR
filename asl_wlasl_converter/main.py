#!/usr/bin/env python
"""
ASL WLASL Converter - Main Interface

This script provides a command-line interface for converting between:
1. Text to ASL video
2. ASL video to text

It sets up the necessary components and provides a unified interface.
"""

import os
import sys
import argparse
import tempfile
from typing import List, Dict, Tuple, Optional

from dataset_utils import WLASLDataset, text_to_gloss
from text_to_video import create_asl_video_from_text
from video_to_text import recognize_signs_from_video


def validate_paths(args):
    """Validate input paths exist."""
    if hasattr(args, 'json') and not os.path.exists(args.json):
        print(f"Error: JSON file not found: {args.json}")
        return False
        
    if hasattr(args, 'videos') and not os.path.exists(args.videos):
        # Try the archive-3 path if the provided path doesn't exist
        archive3_videos_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'archive-3', 'videos')
        if os.path.exists(archive3_videos_path):
            print(f"Using videos from archive-3: {archive3_videos_path}")
            args.videos = archive3_videos_path
        else:
            print(f"Error: Videos directory not found: {args.videos}")
            return False
    
    if hasattr(args, 'video') and args.video and not os.path.exists(args.video):
        print(f"Error: Video file not found: {args.video}")
        return False
        
    if hasattr(args, 'model') and args.model and not os.path.exists(args.model):
        print(f"Error: Model file not found: {args.model}")
        # Don't return False here as the model path is optional in some cases
        
    return True


def text_to_video_command(args):
    """Handle the text-to-video command."""
    if not validate_paths(args):
        return
    
    # Create dataset
    dataset = WLASLDataset(args.json, args.videos)
    
    # Create ASL video
    output_path = create_asl_video_from_text(
        args.text,
        dataset,
        args.output,
        include_transitions=not args.no_transitions,
        resize_videos=not args.no_resize
    )
    
    if output_path:
        print(f"\nSuccessfully created ASL video: {output_path}")
        
        # Optionally recognize the video we just created
        if args.recognize:
            print("\nRecognizing signs from the created video:")
            model_path = args.model if hasattr(args, 'model') and args.model else None
            
            if not model_path:
                print("Warning: No model path provided for recognition.")
                print("Using a placeholder implementation.")
            
            predictions = recognize_signs_from_video(
                output_path,
                dataset,
                model_path,
                args.top_k
            )
            
            print("\nTop predictions:")
            for i, (word, confidence) in enumerate(predictions):
                print(f"{i+1}. {word} ({confidence:.4f})")


def video_to_text_command(args):
    """Handle the video-to-text command."""
    if not validate_paths(args):
        return
    
    # Create dataset
    dataset = WLASLDataset(args.json, args.videos)
    
    # Recognize signs
    predictions = recognize_signs_from_video(
        args.video,
        dataset,
        args.model,
        args.top_k
    )
    
    # Print predictions
    print("\nTop predictions:")
    for i, (word, confidence) in enumerate(predictions):
        print(f"{i+1}. {word} ({confidence:.4f})")


def random_video_command(args):
    """Handle the random-video command."""
    if not validate_paths(args):
        return
    
    # Create dataset
    dataset = WLASLDataset(args.json, args.videos)
    
    # Get a random word and video
    word, video_filename = dataset.get_random_video()
    video_path = dataset.get_video_path(video_filename)
    
    print(f"Selected random sign: '{word}'")
    print(f"Video file: {video_filename}")
    
    # Optionally copy the video to the output path
    if args.output:
        import shutil
        shutil.copy(video_path, args.output)
        print(f"Copied video to: {args.output}")
    
    # Optionally recognize the video
    if args.recognize:
        print("\nRecognizing signs from the selected video:")
        model_path = args.model if hasattr(args, 'model') and args.model else None
        
        if not model_path:
            print("Warning: No model path provided for recognition.")
            print("Using a placeholder implementation.")
        
        predictions = recognize_signs_from_video(
            video_path,
            dataset,
            model_path,
            args.top_k
        )
        
        print("\nTop predictions:")
        for i, (word, confidence) in enumerate(predictions):
            print(f"{i+1}. {word} ({confidence:.4f})")


def main():
    """Main function to run the ASL WLASL converter."""
    parser = argparse.ArgumentParser(description="ASL WLASL Converter")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Text to Video command
    text_to_video_parser = subparsers.add_parser("text-to-video", help="Convert text to ASL video")
    text_to_video_parser.add_argument("--text", type=str, required=True, help="English text to convert to ASL")
    text_to_video_parser.add_argument("--json", type=str, required=True, help="Path to WLASL JSON file")
    text_to_video_parser.add_argument("--videos", type=str, required=True, help="Path to WLASL videos directory")
    text_to_video_parser.add_argument("--output", type=str, required=True, help="Output video path")
    text_to_video_parser.add_argument("--no-transitions", action="store_true", help="Disable fade transitions")
    text_to_video_parser.add_argument("--no-resize", action="store_true", help="Disable video resizing")
    text_to_video_parser.add_argument("--recognize", action="store_true", help="Recognize signs from the created video")
    text_to_video_parser.add_argument("--model", type=str, help="Path to pretrained I3D model (for recognition)")
    text_to_video_parser.add_argument("--top-k", type=int, default=5, help="Number of top predictions to show")
    
    # Video to Text command
    video_to_text_parser = subparsers.add_parser("video-to-text", help="Recognize ASL signs from video")
    video_to_text_parser.add_argument("--video", type=str, required=True, help="Path to input video file")
    video_to_text_parser.add_argument("--json", type=str, required=True, help="Path to WLASL JSON file")
    video_to_text_parser.add_argument("--videos", type=str, required=True, help="Path to WLASL videos directory")
    video_to_text_parser.add_argument("--model", type=str, required=True, help="Path to pretrained I3D model")
    video_to_text_parser.add_argument("--top-k", type=int, default=5, help="Number of top predictions to show")
    
    # Random Video command
    random_video_parser = subparsers.add_parser("random-video", help="Select a random video from the dataset")
    random_video_parser.add_argument("--json", type=str, required=True, help="Path to WLASL JSON file")
    random_video_parser.add_argument("--videos", type=str, required=True, help="Path to WLASL videos directory")
    random_video_parser.add_argument("--output", type=str, help="Output path to copy the random video to")
    random_video_parser.add_argument("--recognize", action="store_true", help="Recognize signs from the random video")
    random_video_parser.add_argument("--model", type=str, help="Path to pretrained I3D model (for recognition)")
    random_video_parser.add_argument("--top-k", type=int, default=5, help="Number of top predictions to show")
    
    args = parser.parse_args()
    
    if args.command == "text-to-video":
        text_to_video_command(args)
    elif args.command == "video-to-text":
        video_to_text_command(args)
    elif args.command == "random-video":
        random_video_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()