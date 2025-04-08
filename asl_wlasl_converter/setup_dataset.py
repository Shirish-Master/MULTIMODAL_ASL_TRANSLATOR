#!/usr/bin/env python
"""
Setup WLASL Dataset

This script helps set up the WLASL dataset for use with the ASL WLASL Converter.
It downloads the JSON metadata file and provides instructions for downloading videos.
"""

import os
import sys
import argparse
import requests
import json
from pathlib import Path


def setup_wlasl_metadata(output_dir):
    """
    Download the WLASL JSON metadata file.
    
    Args:
        output_dir: Directory to save the metadata file
    
    Returns:
        Path to the downloaded file, or None if download failed
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # URL for the WLASL JSON metadata
    # Note: This is a placeholder URL - in a real implementation,
    # you would need to provide the actual URL or include the file
    json_url = "https://raw.githubusercontent.com/dxli94/WLASL/master/start_kit/WLASL_v0.3.json"
    
    output_path = os.path.join(output_dir, "WLASL_v0.3.json")
    
    try:
        print(f"Downloading WLASL metadata from {json_url}...")
        
        # Note: In a real implementation, you would do:
        # response = requests.get(json_url)
        # with open(output_path, 'wb') as f:
        #     f.write(response.content)
        
        # For now, create a minimal JSON file with a few sample entries
        print("Note: This is a placeholder implementation that creates a sample JSON file.")
        print("In a real setup, you would download the actual WLASL metadata.")
        
        sample_data = [
            {
                "gloss": "book",
                "instances": [
                    {
                        "instance_id": 0,
                        "video_id": "00335",
                        "split": "train"
                    }
                ]
            },
            {
                "gloss": "learn",
                "instances": [
                    {
                        "instance_id": 1,
                        "video_id": "00583",
                        "split": "train"
                    }
                ]
            },
            {
                "gloss": "want",
                "instances": [
                    {
                        "instance_id": 2,
                        "video_id": "00832",
                        "split": "train"
                    }
                ]
            }
        ]
        
        with open(output_path, 'w') as f:
            json.dump(sample_data, f, indent=4)
        
        print(f"Created sample metadata file at {output_path}")
        
        return output_path
    
    except Exception as e:
        print(f"Error downloading WLASL metadata: {e}")
        return None


def print_video_download_instructions(json_path, videos_dir):
    """
    Print instructions for downloading WLASL videos.
    
    Args:
        json_path: Path to the WLASL JSON metadata file
        videos_dir: Directory to save the videos
    """
    print("\nTo download WLASL videos:")
    print("-------------------------")
    print(f"1. Create a directory for the videos: {videos_dir}")
    print("2. Visit the WLASL repository: https://github.com/dxli94/WLASL")
    print("3. Follow their instructions for downloading videos")
    print("4. Place the videos in the videos directory")
    print("\nNote: The videos should be named according to their video_id in the JSON file.")
    print("For example, for video_id '00123', the filename should be '00123.mp4'.")
    print("\nFor a quick test, you can download a few sample videos:")
    
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        print("\nSample videos to download:")
        for i, entry in enumerate(data[:5]):  # Show first 5 entries
            gloss = entry['gloss']
            for instance in entry['instances'][:2]:  # Show first 2 instances per gloss
                if 'video_id' in instance:
                    video_id = instance['video_id']
                    print(f"- {video_id}.mp4 (sign: {gloss})")
    except:
        print("Could not parse JSON file for sample videos.")


def main():
    """Main function to set up the WLASL dataset."""
    parser = argparse.ArgumentParser(description="Set up WLASL dataset")
    parser.add_argument("--output-dir", type=str, default="data", 
                      help="Directory to save the dataset files")
    
    args = parser.parse_args()
    
    # Create data directory structure
    data_dir = args.output_dir
    videos_dir = os.path.join(data_dir, "videos")
    
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(videos_dir, exist_ok=True)
    
    # Download WLASL metadata
    json_path = setup_wlasl_metadata(data_dir)
    
    if json_path:
        print_video_download_instructions(json_path, videos_dir)
        
        print("\nOnce you have downloaded the videos, you can use the ASL WLASL Converter:")
        print(f"python main.py text-to-video --text \"I want to learn\" --json {json_path} --videos {videos_dir} --output output.mp4")


if __name__ == "__main__":
    main()