"""
ASL WLASL Converter Web Application

A Flask-based web interface for the ASL WLASL Converter.
Features:
- Text to ASL Video conversion
- ASL Video to Text recognition
- Random ASL Video selection
"""

import os
import sys
import json
import uuid
import tempfile
from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename

# Add parent directory to path to import converter modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from dataset_utils import WLASLDataset, text_to_gloss
    from text_to_video import create_asl_video_from_text
    from video_to_text import recognize_signs_from_video
except ModuleNotFoundError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all required packages are installed:")
    print("pip install -r requirements.txt")
    print("Specifically, ensure moviepy is installed correctly:")
    print("pip install moviepy --upgrade")
    sys.exit(1)

app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = os.path.join(current_dir, 'static', 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(current_dir, 'static', 'generated')
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'mov', 'webm'}
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload size

# Constants
DEFAULT_JSON_PATH = os.path.join(parent_dir, 'data', 'WLASL_v0.3.json')
# First try data/videos, then fallback to archive-3/videos
DEFAULT_VIDEOS_DIR = os.path.join(parent_dir, 'data', 'videos')
if not os.path.exists(DEFAULT_VIDEOS_DIR):
    archive3_videos_path = os.path.join(os.path.dirname(parent_dir), 'archive-3', 'videos')
    if os.path.exists(archive3_videos_path):
        DEFAULT_VIDEOS_DIR = archive3_videos_path
DEFAULT_MODEL_PATH = os.path.join(parent_dir, 'models', 'i3d_model.pth')

# Create upload and output directories if they don't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)


def allowed_file(filename):
    """Check if file has allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def get_dataset():
    """Get the WLASL dataset."""
    # Check if JSON file and videos directory exist
    if not os.path.exists(DEFAULT_JSON_PATH):
        return None, "WLASL metadata file not found. Please set up the dataset first."
    
    if not os.path.exists(DEFAULT_VIDEOS_DIR):
        return None, "WLASL videos directory not found. Please set up the dataset first."
    
    try:
        # Initialize dataset
        dataset = WLASLDataset(DEFAULT_JSON_PATH, DEFAULT_VIDEOS_DIR)
        return dataset, None
    except Exception as e:
        return None, f"Error loading WLASL dataset: {str(e)}"


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/api/text-to-video', methods=['POST'])
def api_text_to_video():
    """API endpoint for text to video conversion."""
    if 'text' not in request.form:
        return jsonify({'error': 'No text provided'}), 400
    
    text = request.form['text']
    
    # Get the dataset
    dataset, error = get_dataset()
    if error:
        return jsonify({'error': error}), 500
    
    # Generate a unique filename for the output video
    output_filename = f"asl_{uuid.uuid4().hex}.mp4"
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    
    # Convert text to video
    try:
        # Get options from the request
        include_transitions = request.form.get('transitions', 'true') == 'true'
        resize_videos = request.form.get('resize', 'true') == 'true'
        detect_homonyms = request.form.get('detect_homonyms', 'true') == 'true'
        
        # Create the ASL video
        result_path, homonym_meanings = create_asl_video_from_text(
            text,
            dataset,
            output_path,
            include_transitions=include_transitions,
            resize_videos=resize_videos,
            detect_homonyms_enabled=detect_homonyms
        )
        
        if result_path:
            # Get the glossed text for display
            glossed_text = text_to_gloss(text)
            
            # Return success response
            return jsonify({
                'status': 'success',
                'video_url': url_for('static', filename=f'generated/{output_filename}'),
                'glossed_text': glossed_text,
                'homonym_meanings': homonym_meanings
            })
        else:
            return jsonify({'error': 'Failed to create ASL video. Check logs for details.'}), 500
    
    except Exception as e:
        return jsonify({'error': f'Error creating ASL video: {str(e)}'}), 500


@app.route('/api/video-to-text', methods=['POST'])
def api_video_to_text():
    """API endpoint for video to text conversion."""
    # Check if a file was uploaded
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    
    # Check if the file is empty
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Check if the file has an allowed extension
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed types: mp4, avi, mov, webm'}), 400
    
    # Get the dataset
    dataset, error = get_dataset()
    if error:
        return jsonify({'error': error}), 500
    
    try:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Get the number of top predictions to return
        top_k = int(request.form.get('top_k', 5))
        
        # Recognize signs from the video
        predictions = recognize_signs_from_video(
            file_path,
            dataset,
            DEFAULT_MODEL_PATH,
            top_k
        )
        
        # Return success response
        return jsonify({
            'status': 'success',
            'predictions': [{'word': word, 'confidence': float(confidence)} for word, confidence in predictions]
        })
    
    except Exception as e:
        return jsonify({'error': f'Error recognizing signs: {str(e)}'}), 500


@app.route('/api/random-video', methods=['POST'])
def api_random_video():
    """API endpoint for getting a random video."""
    # Get the dataset
    dataset, error = get_dataset()
    if error:
        return jsonify({'error': error}), 500
    
    try:
        # Get a random word and video
        word, video_filename = dataset.get_random_video()
        video_path = dataset.get_video_path(video_filename)
        
        # Copy the video to the output folder
        output_filename = f"random_{uuid.uuid4().hex}.mp4"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        # Use ffmpeg to copy the video (allows conversion if needed)
        os.system(f"ffmpeg -i '{video_path}' -c copy '{output_path}' -y >/dev/null 2>&1")
        
        # Check if the model exists
        recognize = request.form.get('recognize', 'false') == 'true'
        predictions = []
        
        if recognize:
            # Get the number of top predictions to return
            top_k = int(request.form.get('top_k', 5))
            
            # Recognize signs from the video
            predictions = recognize_signs_from_video(
                video_path,
                dataset,
                DEFAULT_MODEL_PATH,
                top_k
            )
            predictions = [{'word': word, 'confidence': float(confidence)} for word, confidence in predictions]
        
        # Return success response
        return jsonify({
            'status': 'success',
            'word': word,
            'video_url': url_for('static', filename=f'generated/{output_filename}'),
            'predictions': predictions
        })
    
    except Exception as e:
        return jsonify({'error': f'Error getting random video: {str(e)}'}), 500


@app.route('/api/dataset-info', methods=['GET'])
def api_dataset_info():
    """API endpoint for getting dataset information."""
    # Get the dataset
    dataset, error = get_dataset()
    if error:
        return jsonify({'error': error}), 500
    
    try:
        # Get dataset information
        available_words = dataset.get_available_words()
        sample_words = available_words[:10] if len(available_words) > 10 else available_words
        
        # Return success response
        return jsonify({
            'status': 'success',
            'word_count': len(available_words),
            'sample_words': sample_words,
            'is_model_available': os.path.exists(DEFAULT_MODEL_PATH)
        })
    
    except Exception as e:
        return jsonify({'error': f'Error getting dataset information: {str(e)}'}), 500


@app.route('/setup')
def setup():
    """Render the setup page."""
    return render_template('setup.html')


@app.route('/api/setup-check', methods=['GET'])
def api_setup_check():
    """API endpoint for checking setup status."""
    # Check if JSON file and videos directory exist
    json_exists = os.path.exists(DEFAULT_JSON_PATH)
    videos_dir_exists = os.path.exists(DEFAULT_VIDEOS_DIR)
    model_exists = os.path.exists(DEFAULT_MODEL_PATH)
    
    # Count videos if directory exists
    video_count = 0
    if videos_dir_exists:
        video_files = [f for f in os.listdir(DEFAULT_VIDEOS_DIR) if f.lower().endswith(('.mp4', '.avi', '.mov', '.webm'))]
        video_count = len(video_files)
    
    # Return status
    return jsonify({
        'status': 'success',
        'json_exists': json_exists,
        'videos_dir_exists': videos_dir_exists,
        'model_exists': model_exists,
        'video_count': video_count,
        'json_path': DEFAULT_JSON_PATH,
        'videos_dir': DEFAULT_VIDEOS_DIR,
        'model_path': DEFAULT_MODEL_PATH
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)