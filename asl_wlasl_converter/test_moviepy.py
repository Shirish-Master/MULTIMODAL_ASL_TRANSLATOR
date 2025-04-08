#!/usr/bin/env python3

"""
Simple script to test if MoviePy is correctly installed.
"""

import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

try:
    import moviepy
    print(f"MoviePy version: {moviepy.__version__}")
    print(f"MoviePy path: {moviepy.__file__}")
    
    # Try importing specific modules
    try:
        from moviepy.editor import VideoFileClip, concatenate_videoclips
        print("Successfully imported VideoFileClip and concatenate_videoclips")
    except ImportError as e:
        print(f"Error importing from moviepy.editor: {e}")
    
    # Check available modules
    print("\nAvailable modules in moviepy:")
    for module in dir(moviepy):
        if not module.startswith('_'):
            print(f"- {module}")
    
    # Check if editor exists
    if hasattr(moviepy, 'editor'):
        print("\nAvailable in moviepy.editor:")
        for item in dir(moviepy.editor):
            if not item.startswith('_'):
                print(f"- {item}")
    
except ImportError as e:
    print(f"Error importing MoviePy: {e}")
    
print("\nPython Path:")
for path in sys.path:
    print(f"- {path}")