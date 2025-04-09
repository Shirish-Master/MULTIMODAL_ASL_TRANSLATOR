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
    # Import core modules
    from dataset_utils import WLASLDataset, text_to_gloss
    from text_to_video import create_asl_video_from_text
    from video_to_text import recognize_signs_from_video
    
    # Import moviepy modules directly (necessary for compatibility)
    try:
        # Try importing directly from moviepy.editor
        from moviepy.editor import VideoFileClip, concatenate_videoclips
    except ImportError:
        try:
            # Try the older import path
            import moviepy.editor as mpy
            VideoFileClip = mpy.VideoFileClip
            concatenate_videoclips = mpy.concatenate_videoclips
        except ImportError:
            # Direct import as last resort
            import moviepy
            from moviepy import VideoFileClip, concatenate_videoclips
            
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

# Load API key from config.py file (which is gitignored)
try:
    # Try to import from config.py file
    import sys
    sys.path.append(parent_dir)
    from config import OPENAI_API_KEY
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    print("Loaded API key from config.py file")
except ImportError:
    # Fallback to a placeholder value
    os.environ["OPENAI_API_KEY"] = "your-api-key-here"
    print("Using placeholder API key - please configure in config.py file")

# Constants
# First check if the JSON file exists in archive-3
archive3_json_path = os.path.join(os.path.dirname(parent_dir), 'archive-3', 'WLASL_v0.3.json')
if os.path.exists(archive3_json_path):
    DEFAULT_JSON_PATH = archive3_json_path
else:
    DEFAULT_JSON_PATH = os.path.join(parent_dir, 'data', 'WLASL_v0.3.json')
# First try archive-3/videos, then fallback to data/videos
archive3_videos_path = os.path.join(os.path.dirname(parent_dir), 'archive-3', 'videos')
if os.path.exists(archive3_videos_path):
    DEFAULT_VIDEOS_DIR = archive3_videos_path
else:
    DEFAULT_VIDEOS_DIR = os.path.join(parent_dir, 'data', 'videos')
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
        # Print paths for debugging
        print(f"Using JSON file: {DEFAULT_JSON_PATH}")
        print(f"Using videos directory: {DEFAULT_VIDEOS_DIR}")
        
        # Initialize dataset
        dataset = WLASLDataset(DEFAULT_JSON_PATH, DEFAULT_VIDEOS_DIR)
        
        # Verify we have at least some videos
        available_words = dataset.get_available_words()
        if not available_words:
            return None, "No videos found in the dataset. Please check the videos directory."
            
        print(f"Dataset loaded successfully with {len(available_words)} available words")
        return dataset, None
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None, f"Error loading WLASL dataset: {str(e)}"


@app.route('/')
def index():
    """Render the main page."""
    # Check if OpenAI API key is set for homonym detection
    openai_api_key = os.environ.get("OPENAI_API_KEY", "")
    has_api_key = bool(openai_api_key) and openai_api_key != "your-api-key-here"
    
    # If hardcoded key is still the placeholder, show a special message
    is_placeholder = openai_api_key == "your-api-key-here"
    
    return render_template('index.html', has_api_key=has_api_key, is_placeholder=is_placeholder)


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
        
        # Convert text to gloss
        glossed_text = text_to_gloss(text)
        
        # Handle homonym detection if enabled
        homonym_meanings = {}
        if detect_homonyms:
            try:
                # Check if API key is set
                openai_api_key = os.environ.get("OPENAI_API_KEY", "")
                if not openai_api_key:
                    homonym_meanings = {"raw_response": "No OpenAI API key set. Please set it on the Setup page."}
                    print("No OpenAI API key set")
                elif openai_api_key == "your-api-key-here":
                    homonym_meanings = {"raw_response": "Please replace the placeholder API key with your actual OpenAI API key."}
                    print("API key is still the placeholder value")
                else:
                    print(f"Using OpenAI API for homonym detection with text: '{text}'")
                    from text_to_video import detect_homonyms
                    homonym_meanings = detect_homonyms(text, glossed_text)
                
                # If no OpenAI API key, provide sample homonyms for demo purposes
                if not homonym_meanings:
                    # Process all possible homonyms in the text
                    homonym_list = ["bank", "bat", "bear", "bow", "light", "star", "tie", "saw", "ring", "kind", "fair", "present", "rock", "spring", "letter"]
                    
                    # Keep track of which homonyms were found
                    found_homonyms = []
                    
                    # Check for common homonyms for demo purposes
                    for word in glossed_text:
                        word_lower = word.lower()
                        if word_lower in homonym_list:
                            found_homonyms.append(word_lower)
                            
                    # Only proceed if we found some homonyms
                    if found_homonyms:
                        print(f"Found homonyms in demo mode: {found_homonyms}")
                        
                        # Process each found homonym
                        for word_lower in found_homonyms:
                            if word_lower == "bank":
                                homonym_meanings[word_lower] = "financial institution" if "money" in text.lower() else "river edge"
                            elif word_lower == "bat":
                                homonym_meanings[word_lower] = "animal" if "fly" in text.lower() else "baseball equipment"
                            elif word_lower == "bow":
                                homonym_meanings[word_lower] = "bend forward" if "respect" in text.lower() else "tie ribbon"
                            elif word_lower == "light":
                                homonym_meanings[word_lower] = "not heavy" if "weight" in text.lower() else "illumination"
                            elif word_lower == "star":
                                homonym_meanings[word_lower] = "celestial body" if "sky" in text.lower() else "celebrity"
                            elif word_lower == "tie":
                                homonym_meanings[word_lower] = "neck accessory" if "shirt" in text.lower() else "to fasten"
                            elif word_lower == "saw":
                                homonym_meanings[word_lower] = "cutting tool" if "wood" in text.lower() else "past tense of see"
                            elif word_lower == "ring":
                                homonym_meanings[word_lower] = "jewelry" if "finger" in text.lower() else "sound"
                            elif word_lower == "present":
                                homonym_meanings[word_lower] = "gift" if "birthday" in text.lower() else "current time"
                            elif word_lower == "spring":
                                homonym_meanings[word_lower] = "season" if "summer" in text.lower() or "winter" in text.lower() else "coil"
                            elif word_lower == "rock":
                                homonym_meanings[word_lower] = "stone" if "hard" in text.lower() or "ground" in text.lower() else "music genre"
                            elif word_lower == "fair":
                                homonym_meanings[word_lower] = "just" if "equal" in text.lower() or "justice" in text.lower() else "carnival"
                            elif word_lower == "kind":
                                homonym_meanings[word_lower] = "nice" if "gentle" in text.lower() or "good" in text.lower() else "type"
                            elif word_lower == "letter":
                                homonym_meanings[word_lower] = "mail" if "post" in text.lower() or "send" in text.lower() else "alphabet character"
                        
                    # Ensure all values are strings
                    for key in list(homonym_meanings.keys()):
                        if not isinstance(homonym_meanings[key], str):
                            homonym_meanings[key] = str(homonym_meanings[key])
                
                if homonym_meanings:
                    print(f"Detected homonyms with meanings: {homonym_meanings}")
            except Exception as e:
                print(f"Error in homonym detection: {e}")
        
        # Find videos for each word
        video_paths = []
        missing_words = []
        
        for word in glossed_text:
            video_filename = dataset.get_video_for_word(word)
            if video_filename:
                video_path = dataset.get_video_path(video_filename)
                if os.path.exists(video_path):
                    video_paths.append(video_path)
                    print(f"Found video for '{word}': {video_filename}")
                else:
                    missing_words.append(word)
                    print(f"Video file not found: {video_path}")
            else:
                missing_words.append(word)
                print(f"No video found for '{word}'")
        
        if not video_paths:
            return jsonify({
                'status': 'error',
                'error': f'No videos found for any words in: {text}',
                'glossed_text': glossed_text,
                'missing_words': missing_words
            }), 400
        
        # Create clips from video paths
        clips = []
        for path in video_paths:
            clip = VideoFileClip(path)
            if resize_videos:
                try:
                    # Different versions of MoviePy have different resize APIs
                    if hasattr(clip, 'resize_width'):
                        clip = clip.resize_width(640)
                    elif hasattr(clip, 'resize'):
                        clip = clip.resize((640, 480))
                    elif hasattr(clip, 'resize_height'):
                        clip = clip.resize_height(480)
                    else:
                        # Last resort - use the clip's fx method
                        from moviepy.video.fx import resize
                        clip = resize.resize(clip, width=640, height=480)
                except Exception as e:
                    print(f"Error resizing clip: {e}")
            clips.append(clip)
        
        # Concatenate clips
        try:
            if include_transitions and len(clips) > 1:
                final_clip = concatenate_videoclips(clips, method="compose")
            else:
                final_clip = concatenate_videoclips(clips, method="chain")
            
            # Write the video
            final_clip.write_videofile(output_path, codec="libx264", audio=False)
            
            # Clean up
            for clip in clips:
                clip.close()
            final_clip.close()
            
            # Homonym meanings were already detected earlier
            
            # Ensure homonym_meanings is included even if empty
            if not homonym_meanings:
                homonym_meanings = {"raw_response": "Error: No response received from OpenAI API. Make sure your API key is valid and has sufficient credits."}
                
            # Return success response
            return jsonify({
                'status': 'success',
                'video_url': url_for('static', filename=f'generated/{output_filename}'),
                'glossed_text': glossed_text,
                'homonym_meanings': homonym_meanings,
                'missing_words': missing_words
            })
            
        except Exception as e:
            # Clean up any open clips
            for clip in clips:
                try:
                    clip.close()
                except:
                    pass
            
            return jsonify({
                'status': 'error',
                'error': f'Error creating video: {str(e)}',
                'glossed_text': glossed_text,
                'missing_words': missing_words
            }), 500
    
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


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """Render the setup page."""
    # Handle API key submission
    message = None
    if request.method == 'POST' and 'openai_api_key' in request.form:
        api_key = request.form['openai_api_key'].strip()
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            message = "OpenAI API key has been set successfully!"
        else:
            message = "Please provide a valid API key."
    
    # Check if key is currently set
    has_api_key = bool(os.environ.get("OPENAI_API_KEY", ""))
    
    return render_template('setup.html', has_api_key=has_api_key, message=message)


@app.route('/api/test-openai', methods=['GET'])
def api_test_openai():
    """API endpoint for testing OpenAI API key."""
    openai_api_key = os.environ.get("OPENAI_API_KEY", "")
    
    if not openai_api_key:
        return jsonify({
            'status': 'error',
            'message': 'No OpenAI API key set'
        }), 400
    
    if openai_api_key == "your-api-key-here":
        return jsonify({
            'status': 'error',
            'message': 'API key is still set to the placeholder value'
        }), 400
    
    # Try a simple API call
    try:
        import requests
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}"
        }
        
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": "Say hello"}
            ],
            "max_tokens": 10
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'status': 'success',
                'message': 'OpenAI API key is working',
                'response': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'API request failed with status code {response.status_code}',
                'details': response.text
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error testing OpenAI API: {str(e)}'
        }), 500


@app.route('/api/setup-check', methods=['GET'])
def api_setup_check():
    """API endpoint for checking setup status."""
    # Check if JSON file and videos directory exist
    json_exists = os.path.exists(DEFAULT_JSON_PATH)
    videos_dir_exists = os.path.exists(DEFAULT_VIDEOS_DIR)
    model_exists = os.path.exists(DEFAULT_MODEL_PATH)
    
    # Check if OpenAI API key is set
    openai_api_key = os.environ.get("OPENAI_API_KEY", "")
    has_api_key = bool(openai_api_key)
    
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
        'model_path': DEFAULT_MODEL_PATH,
        'has_api_key': has_api_key
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)