# ASL WLASL Converter

A tool for bidirectional conversion between English text and ASL videos using the WLASL dataset.

## Features

- **Text to ASL Video**: Convert English text to ASL videos by stitching together signs from the WLASL dataset
- **Homonym Detection**: Identify and appropriately sign words with multiple meanings based on context
- **ASL Video to Text**: Recognize ASL signs from videos using a pretrained I3D model
- **Random Video Selection**: Select random videos from the WLASL dataset for testing
- **Web Interface**: User-friendly web application for all features

## Requirements

- Python 3.7+
- WLASL dataset (JSON metadata and video files)
- I3D pretrained model for sign recognition (optional)
- Flask (for web application)
- OpenAI API key (for homonym detection)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/asl-wlasl-converter.git
   cd asl-wlasl-converter
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Download the WLASL dataset and pretrained model:
   - WLASL dataset: Visit the [WLASL repository](https://github.com/dxli94/WLASL) for download instructions
   - Pretrained I3D model: Available in the WLASL repository

4. Organize the WLASL dataset:
   - Place the `WLASL_v0.3.json` file in the `data/` directory
   - Place the video files in the `data/videos/` directory
   - Place the I3D model in the `models/` directory (optional, for recognition)

## Web Application

The web application provides a user-friendly interface for all features.

### Running the Web Application

Run the web application with:

```bash
./run_webapp.sh
```

Or manually:

```bash
cd webapp
python app.py
```

Then open `http://localhost:5000` in your browser.

### Web Application Features

- **Text to ASL Video**: Convert text to ASL videos with options for transitions and resizing
- **ASL Video to Text**: Upload videos for sign recognition
- **Random Video**: Select and view random ASL videos from the dataset
- **Setup Page**: Check dataset and model status and get setup instructions

## Command-Line Usage

### Text to ASL Video Conversion

```bash
python main.py text-to-video \
  --text "I want to learn sign language" \
  --json data/WLASL_v0.3.json \
  --videos data/videos \
  --output output_video.mp4 \
  --api-key YOUR_OPENAI_API_KEY
```

Options:
- `--no-transitions`: Disable fade transitions between clips
- `--no-resize`: Keep original video dimensions (may result in size changes between clips)
- `--no-homonym-detection`: Disable homonym detection (faster, but less accurate for ambiguous words)
- `--api-key`: OpenAI API key for homonym detection (can also be set as OPENAI_API_KEY environment variable)
- `--recognize`: Recognize signs from the created video (requires model path)
- `--model`: Path to pretrained I3D model for recognition
- `--top-k`: Number of top predictions to show (default: 5)

### ASL Video to Text Recognition

```bash
python main.py video-to-text \
  --video input_video.mp4 \
  --json data/WLASL_v0.3.json \
  --videos data/videos \
  --model models/i3d_model.pth
```

Options:
- `--top-k`: Number of top predictions to show (default: 5)

### Random Video Selection

```bash
python main.py random-video \
  --json data/WLASL_v0.3.json \
  --videos data/videos
```

Options:
- `--output`: Output path to copy the random video to
- `--recognize`: Recognize signs from the random video
- `--model`: Path to pretrained I3D model for recognition
- `--top-k`: Number of top predictions to show (default: 5)

## Dataset Setup

The `setup_dataset.py` script helps set up the WLASL dataset:

```bash
python setup_dataset.py
```

This creates a sample JSON file and provides instructions for downloading videos.

## Customization

### Adding a "Space" Sign for Segmentation

To implement segmentation using a "space" sign:

1. Record or find videos of the "space" sign
2. Add these videos to your WLASL dataset with the gloss "space"
3. Update the JSON metadata to include the "space" sign
4. Implement segmentation logic in your application

### Text to Gloss Conversion

The current implementation uses a simple approach to convert English text to ASL gloss. 
For more sophisticated conversion, consider implementing a rule-based or machine learning approach.

## Homonym Detection

The homonym detection feature identifies words with multiple meanings and selects the appropriate sign based on context. This is crucial for accurate ASL translation, as many English words have different signs depending on their meaning.

### Examples

- "I saw a bat flying at night" → The sign for "bat" as an animal is used
- "He hit the ball with a bat" → The sign for "bat" as sports equipment is used
- "The bank closed early today" → The sign for "bank" as a financial institution is used
- "We sat by the bank of the river" → The sign for "bank" as the edge of a river is used

### How It Works

1. The system identifies potential homonyms in the input text
2. It uses OpenAI's API to analyze the context and determine the specific meaning
3. The meaning is logged and can be used to select the appropriate sign video

### Setup

To use homonym detection:

1. Get an OpenAI API key from https://platform.openai.com/
2. Set the key as an environment variable:
   ```
   export OPENAI_API_KEY=your_api_key_here
   ```
3. Or pass it directly when running the command:
   ```
   python main.py text-to-video --text "I saw a bat" --api-key YOUR_KEY
   ```

## Limitations

- The current implementation requires manually adding "space" signs between words
- Sign recognition requires the I3D model from the WLASL repository
- Text-to-gloss conversion is simplified and doesn't account for full ASL grammar
- Video stitching may result in visual inconsistencies due to different signers
- Homonym detection is limited by the available signs in the WLASL dataset
- Context-specific sign selection requires extending the dataset with meaning annotations

## Future Improvements

- Implement proper ASL grammar for text-to-gloss conversion
- Add style transfer for visual consistency in stitched videos
- Improve sign recognition with more advanced models
- Add support for continuous sign language recognition
- Implement real-time webcam recognition
- Extend the dataset with meaning annotations for homonyms
- Create a visual indicator for homonym meanings in the generated videos

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [WLASL Dataset](https://github.com/dxli94/WLASL)
- The sign language community
- Contributors to the WLASL research
