#!/usr/bin/env python3

"""
Test direct imports from moviepy.
"""

import sys
print(f"Python version: {sys.version}")

try:
    import moviepy
    print(f"MoviePy version: {moviepy.__version__}")

    # Try direct imports
    try:
        from moviepy import VideoFileClip
        print("Successfully imported VideoFileClip directly")
    except ImportError as e:
        print(f"Error importing VideoFileClip directly: {e}")
    
    try:
        from moviepy import concatenate_videoclips
        print("Successfully imported concatenate_videoclips directly")
    except ImportError as e:
        print(f"Error importing concatenate_videoclips directly: {e}")
        
    # Print all available names at the top level
    print("\nAll top-level names in moviepy:")
    for name in dir(moviepy):
        if not name.startswith('_'):
            print(f"- {name}")
            
except ImportError as e:
    print(f"Error importing MoviePy: {e}")