# ASL-WLASL Converter: Detailed Implementation Specifications

## Exact Technologies and Libraries Used

### Core Technologies
- **Programming Language**: Python 3.7+
- **Web Framework**: Flask 2.0.0
- **Video Processing**: MoviePy 1.0.3, OpenCV 4.5.0
- **Frontend**: HTML5, CSS3 (Bootstrap 5.3), JavaScript (ES6)
- **Data Format**: JSON for dataset and API responses
- **AI Integration**: OpenAI API for homonym detection and context analysis

### External Dependencies
| Library       | Version  | Purpose                                           |
|---------------|----------|---------------------------------------------------|
| Flask         | 2.0.0+   | Web application framework                         |
| Werkzeug      | 2.0.0+   | WSGI utilities for Flask                          |
| MoviePy       | 1.0.3+   | Video editing and concatenation                   |
| OpenCV        | 4.5.0+   | Computer vision and video frame processing        |
| NumPy         | 1.19.0+  | Numerical computing and array operations          |
| Pillow        | 8.0.0+   | Image processing                                  |
| Requests      | 2.25.0+  | HTTP requests for API calls                       |
| tqdm          | 4.50.0+  | Progress bars for long-running operations         |
| OpenAI        | 0.27.0+  | Homonym detection through AI models               |
| python-dotenv | 0.10.0+  | Environment variable management for API keys      |

## Text to ASL Video: Detailed Implementation

### 1. Text Processing Engine

#### Text Normalization
```python
def normalize_text(text):
    """Convert text to lowercase and remove punctuation."""
    text = text.lower()
    text = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in text)
    return text
```

#### Tokenization Strategy
- **Method**: Simple whitespace-based tokenization
- **Implementation**: Python's `split()` function
- **Future Enhancement**: Could use NLTK or spaCy for more advanced tokenization

#### Function Word Filtering
```python
# Exact set of function words filtered from ASL
skip_words = {
    'a', 'an', 'the',                     # Articles
    'is', 'are', 'am', 'was', 'were',     # Forms of "to be"
    'be', 'been', 'being',                # More "to be" forms
    'to', 'of', 'for',                    # Common prepositions
    'and', 'or', 'but', 'nor', 'so',      # Conjunctions
    'at', 'by', 'in', 'into', 'on',       # More prepositions
    'onto', 'with', 'within', 'without'   # More prepositions
}
```

#### ASL Gloss Creation
- **Current Algorithm**: Word filtering + word order preservation
- **Limitations**: Does not implement true ASL grammar rules (such as topic-comment structure)
- **Example Transformation**: "I want to learn sign language" → "I want learn sign language"

### 2. Video Lookup System

#### Database Access Method
- **Dataset Class**: `WLASLDataset` handles all dataset access
- **Index Structure**: Dictionary mappings from words to video filenames
- **Word Matching**: Case-insensitive exact matching
- **Storage Format**: In-memory dictionaries built from JSON file

#### Video Selection Logic
```python
def get_video_for_word(self, word):
    """Get a random video filename for a given word."""
    word = word.lower()
    if word in self.gloss_to_videos and self.gloss_to_videos[word]:
        return random.choice(self.gloss_to_videos[word])
    return None
```

#### Missing Word Handling
- **Tracking**: List of missing words is maintained
- **Reporting**: Missing words are reported in the UI
- **Continuation Strategy**: Processing continues with available words only

### 3. Video Processing System

#### Video Loading
- **Library**: MoviePy's `VideoFileClip` class
- **Loading Strategy**: Sequential loading of individual clips
- **Format Support**: MP4, AVI, MOV, WEBM

#### Video Resizing
```python
# Resize implementation
if resize_videos:
    try:
        if hasattr(clip, 'resize'):
            clip = clip.resize((640, 480))
        elif hasattr(clip, 'resize_width'):
            clip = clip.resize_width(640)
        else:
            print(f"Warning: Could not resize clip")
    except Exception as e:
        print(f"Error resizing clip: {e}")
```

#### Transition Implementation
- **Transition Type**: CrossFadeTransition (when enabled)
- **Implementation**: `concatenate_videoclips(clips, method="compose")`
- **No Transition Alternative**: `concatenate_videoclips(clips, method="chain")`

#### Encoding Parameters
```python
# Final video writing parameters
final_clip.write_videofile(
    output_path,
    codec="libx264",    # H.264 codec for compression
    audio=False,        # No audio track needed
    fps=30,             # Frame rate (implied from source)
    threads=2,          # Parallel processing threads
    preset='medium'     # Encoding speed/quality balance
)
```

## ASL Video to Text: Detailed Implementation

### 1. Video Input Processing

#### Frame Extraction Method
```python
def extract_frames(video_path, num_frames=64):
    """Extract evenly spaced frames from video."""
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    indices = np.linspace(0, frame_count-1, num_frames, dtype=int)
    
    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
    cap.release()
    return frames
```

#### Preprocessing Steps
1. **Resize**: Frames resized to 224×224 pixels (standard for vision models)
2. **Color Conversion**: BGR to RGB conversion (OpenCV uses BGR by default)
3. **Normalization**: Pixel values divided by 255 to range [0,1]

### 2. Hand Detection Implementation

#### Detection Library
- **Current Implementation**: Simulated detection
- **Proposed Library**: MediaPipe Hands (Google's hand tracking solution)
- **Alternative**: OpenPose for full body keypoint detection

#### Keypoint Extraction
- **Hand Landmarks**: 21 keypoints per hand
- **Confidence Thresholds**: 0.5 for hand detection
- **Processing Pipeline**:
  1. Hand detection in each frame
  2. Landmark extraction for each detected hand
  3. Tracking hand positions across frames

### 3. Recognition Model

#### Model Architecture
- **Current Implementation**: Simulated recognition with categorized words
- **Proposed Model**: I3D (Inflated 3D ConvNet)
- **Alternative Models**: 
  - 3D ResNet
  - SlowFast Networks
  - GCN (Graph Convolutional Network) for skeleton-based recognition

#### Classification Strategy
```python
# Simulated classification logic
sign_categories = {
    "common": ["hello", "thank you", "please", "yes", "no", "good", "bad", "like"],
    "emotions": ["happy", "sad", "angry", "love", "excited", "tired"],
    "questions": ["what", "where", "when", "who", "why", "how"],
    "time": ["now", "later", "before", "after", "today", "tomorrow", "yesterday"],
    "actions": ["go", "come", "eat", "drink", "sleep", "work", "play", "help"]
}

# Primary category selection
primary_category = random.choice(list(sign_categories.keys()))
predictions = []

# Add 2-3 words from primary category with high confidence
primary_words = sign_categories[primary_category]
for i in range(min(3, len(primary_words))):
    confidence = max(0.5, 0.9 - (i * 0.2))
    predictions.append((primary_words[i], confidence))
```

## Database Implementation Details

### WLASL Dataset Structure

#### JSON Schema
```javascript
[
  {
    "gloss": "book",              // English word
    "instances": [
      {
        "video_id": "00335",      // Unique video identifier
        "signer_id": 118,         // Person performing the sign
        "variation_id": 0,        // Variation of the sign
        "fps": 25,                // Video frame rate
        "split": "train",         // Dataset split (train/test)
        "bbox": [385, 37, 885, 720] // Bounding box coordinates
      },
      // More instances of this sign...
    ]
  },
  // More words...
]
```

#### Video Naming Convention
- **Format**: `{video_id}.mp4`
- **Example**: `00335.mp4`
- **Resolution**: Varied (original recordings)
- **Duration**: Typically 1-5 seconds per sign

### Dataset Access Implementation

#### Loading and Indexing
```python
def _build_gloss_to_videos_mapping(self):
    """Build a mapping from gloss (word) to list of video filenames."""
    gloss_to_videos = {}
    
    for entry in self.data:
        gloss = entry['gloss'].lower()
        videos = []
        
        for instance in entry['instances']:
            if 'video_id' in instance:
                video_filename = f"{instance['video_id']}.mp4"
                video_path = os.path.join(self.videos_dir, video_filename)
                if os.path.exists(video_path):
                    videos.append(video_filename)
        
        if videos:  # Only add entry if there are valid videos
            gloss_to_videos[gloss] = videos
    
    return gloss_to_videos
```

#### Video Path Resolution
```python
def get_video_path(self, video_filename):
    """Get the full path for a video filename."""
    return os.path.join(self.videos_dir, video_filename)
```

## Web Application Implementation

### API Endpoints Specification

#### Word Video Endpoint
- **URL**: `/api/word-video`
- **Method**: GET
- **Parameters**: `word` (string)
- **Response Format**:
  ```json
  {
    "status": "success",
    "word": "hello",
    "video_path": "/path/to/video.mp4",
    "gloss": ["hello"]
  }
  ```

#### Sentence to Video Endpoint
- **URL**: `/api/sentence-video`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "sentence": "I want to learn sign language",
    "include_transitions": true,
    "resize_videos": true
  }
  ```
- **Response Format**:
  ```json
  {
    "status": "success",
    "message": "ASL video created successfully",
    "video_url": "/static/generated/asl_sentence_123456.mp4",
    "gloss": ["i", "want", "learn", "sign", "language"],
    "missing_words": []
  }
  ```

#### Video to Text Endpoint
- **URL**: `/api/video-to-text`
- **Method**: POST
- **Form Data**: 
  - `video` (file)
  - `top_k` (integer, default: 3)
- **Response Format**:
  ```json
  {
    "status": "success",
    "message": "Video analysis completed",
    "model_info": "Using MediaPipe for hand pose extraction + MobileNetV2 for classification",
    "predictions": [
      {"word": "hello", "confidence": 0.92},
      {"word": "welcome", "confidence": 0.45},
      {"word": "please", "confidence": 0.12}
    ]
  }
  ```

### Frontend Implementation

#### Word List Loading with Progress
```javascript
// SSE event source for progress updates
const eventSource = new EventSource('/api/word-list-progress');
    
eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    const percent = data.percent;
    
    progressBarInner.style.width = percent + '%';
    progressBarInner.setAttribute('aria-valuenow', percent);
    progressBarInner.textContent = `Loading words... ${percent}%`;
    
    if (percent >= 100) {
        eventSource.close();
    }
};
```

#### Video Player Implementation
```html
<div class="video-container">
    <video id="sentence-video" controls class="img-fluid">
        Your browser does not support the video tag.
    </video>
</div>

<script>
    // Display the created video
    const videoElement = document.getElementById('sentence-video');
    videoElement.src = data.video_url;
    videoElement.load();
    videoElement.play();
</script>
```

## Performance and Optimization Details

### Memory Management

#### Temporary File Handling
```python
# Create temporary directory for processing
temp_dir = tempfile.mkdtemp()
file_path = os.path.join(temp_dir, secure_filename(file.filename))
file.save(file_path)

# Clean up after processing
try:
    os.remove(file_path)
    os.rmdir(temp_dir)
except:
    pass
```

#### Resource Cleanup
```python
# Proper video file handle cleanup
try:
    for clip in clips:
        clip.close()
    final_clip.close()
except Exception as e:
    print(f"Error closing clips: {e}")
```

### Error Handling Implementation

#### Exception Structure
```python
try:
    # Processing code
except Exception as e:
    return jsonify({
        'status': 'error',
        'message': f'Error processing request: {str(e)}',
        'additional_info': {
            'gloss': gloss,
            'missing_words': missing_words
        }
    })
```

#### Validation Logic
```python
def validate_inputs(sentence):
    """Validate user inputs."""
    if not sentence:
        return False, "Empty sentence provided"
    if len(sentence) > 1000:
        return False, "Sentence too long (max 1000 characters)"
    return True, None
```

## Homonym Detection Implementation

### Key Components

#### 1. Homonym Identification
```python
def detect_homonyms(text, words):
    """Detect homonyms in a sentence and determine their meaning."""
    # Common homonyms to check for
    common_homonyms = [
        "bat", "bank", "bark", "bear", "bow", "fair", "kind", 
        "letter", "light", "mean", "might", "present", "ring", 
        "rock", "rose", "saw", "seal", "spring", "star", "tie"
    ]
    
    # Check if any words in the text are homonyms
    potential_homonyms = [word for word in words if word.lower() in common_homonyms]
    
    if not potential_homonyms:
        return {}
```

#### 2. OpenAI API Integration
```python
# API request configuration
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
```

#### 3. Response Parsing
```python
# Extract JSON from API response
import re
import json

if response.status_code == 200:
    result = response.json()
    content = result["choices"][0]["message"]["content"]
    
    # Try to extract JSON from the response
    json_match = re.search(r'{.*}', content, re.DOTALL)
    if json_match:
        meanings = json.loads(json_match.group(0))
        homonym_meanings = meanings
```

#### 4. Context-Based Video Selection
```python
# In create_asl_video_from_text function
for word in gloss:
    # Check if word is a homonym with specific meaning
    specific_meaning = homonym_meanings.get(word.lower())
    
    if specific_meaning:
        print(f"Word '{word}' is a homonym meaning '{specific_meaning}'")
        # Here you would ideally look up the specific meaning video
        # For now, we just log the meaning and use the regular video
        video_filename = dataset.get_video_for_word(word)
    else:
        # Regular word processing (non-homonym)
        video_filename = dataset.get_video_for_word(word)
```

### API Response Example

For the sentence "I saw a bat flying at night":

```json
{
  "bat": "animal"
}
```

For the sentence "He hit the ball with a bat":

```json
{
  "bat": "sports equipment"
}
```

## Future Development Roadmap

### Specific Enhancement Opportunities

1. **Advanced Text Processing**:
   - Integration with NLTK or spaCy for proper linguistic analysis
   - ASL grammar rules implementation based on linguistic research
   - Named entity recognition for proper nouns
   - Improved homonym detection with local models

2. **Video Improvement Techniques**:
   - GANs for style transfer between different signers
   - Frame interpolation for smoother transitions
   - Background normalization across videos
   - Contextual meaning visualization for homonyms

3. **Recognition Improvements**:
   - Fine-tuning pretrained I3D models on WLASL dataset
   - Implementation of attention mechanisms for important hand features
   - Ensemble methods combining skeletal and visual features
   - Homonym disambiguation in video-to-text conversion

---

This document outlines the exact implementation details of the ASL-WLASL Converter system, providing specific code examples, algorithm descriptions, and technical specifications for all major components.