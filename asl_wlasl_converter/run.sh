#!/bin/bash
echo "Starting ASL WLASL Converter Web Application..."
echo "Using direct paths to archive-3 directory for videos and JSON data"
echo "Note: This will use the videos in /Users/yuvan/Documents/Code/AI_testing/claudeCode/MiniProject/archive-3/videos"
cd webapp && python3 simple_app.py
echo "Open http://localhost:8080 in your browser"