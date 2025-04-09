/**
 * ASL WLASL Converter Web Application JavaScript
 * Handles UI interactions and API calls
 */

// DOM Elements
const textToVideoForm = document.getElementById('text-to-video-form');
const videoToTextForm = document.getElementById('video-to-text-form');
const randomVideoBtn = document.getElementById('random-video-btn');
const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Initialize tabs
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            if (link.getAttribute('href').startsWith('#')) {
                event.preventDefault();
                navLinks.forEach(l => l.classList.remove('active'));
                link.classList.add('active');
                
                const targetId = link.getAttribute('href');
                const tabPanes = document.querySelectorAll('.tab-pane');
                tabPanes.forEach(pane => {
                    pane.classList.remove('show', 'active');
                });
                document.querySelector(targetId).classList.add('show', 'active');
            }
        });
    });
    
    // Add event listeners
    textToVideoForm.addEventListener('submit', handleTextToVideo);
    videoToTextForm.addEventListener('submit', handleVideoToText);
    randomVideoBtn.addEventListener('click', handleRandomVideo);
    
    // Load dataset info
    loadDatasetInfo();
});

/**
 * Load and display dataset information
 */
async function loadDatasetInfo() {
    try {
        const response = await fetch('/api/dataset-info');
        const data = await response.json();
        
        if (data.status === 'success') {
            const infoElement = document.getElementById('dataset-info');
            
            if (data.word_count > 0) {
                // Dataset is properly loaded
                infoElement.classList.remove('alert-info');
                infoElement.classList.add('alert-success');
                
                let html = `<h4><i class="fas fa-check-circle me-2"></i>Dataset Ready</h4>`;
                html += `<p>The WLASL dataset is loaded with ${data.word_count} available words.</p>`;
                html += `<p>Sample words: ${data.sample_words.join(', ')}...</p>`;
                
                if (data.is_model_available) {
                    html += `<p><i class="fas fa-check-circle text-success me-2"></i>Pretrained model is available for recognition.</p>`;
                } else {
                    html += `<p><i class="fas fa-exclamation-triangle text-warning me-2"></i>Pretrained model not found. Recognition will use fallback method.</p>`;
                }
                
                infoElement.innerHTML = html;
            } else {
                // Dataset has issues
                infoElement.classList.remove('alert-info');
                infoElement.classList.add('alert-warning');
                
                let html = `<h4><i class="fas fa-exclamation-triangle me-2"></i>Dataset Issues</h4>`;
                html += `<p>The WLASL dataset is available but contains no words.</p>`;
                html += `<p>Please check your dataset setup on the <a href="/setup">Setup Page</a>.</p>`;
                
                infoElement.innerHTML = html;
            }
        } else {
            // Dataset error
            infoElement.classList.remove('alert-info');
            infoElement.classList.add('alert-danger');
            
            let html = `<h4><i class="fas fa-times-circle me-2"></i>Dataset Not Available</h4>`;
            html += `<p>Error: ${data.error || 'Unknown error loading the dataset.'}</p>`;
            html += `<p>Please set up the dataset on the <a href="/setup">Setup Page</a>.</p>`;
            
            infoElement.innerHTML = html;
        }
    } catch (error) {
        // Network or other error
        const infoElement = document.getElementById('dataset-info');
        infoElement.classList.remove('alert-info');
        infoElement.classList.add('alert-danger');
        
        let html = `<h4><i class="fas fa-times-circle me-2"></i>Error</h4>`;
        html += `<p>Could not connect to the server. Please check if the application is running.</p>`;
        
        infoElement.innerHTML = html;
    }
}

/**
 * Handle text to video conversion
 */
async function handleTextToVideo(event) {
    event.preventDefault();
    
    const textInput = document.getElementById('text-input').value.trim();
    if (!textInput) {
        showError('Please enter some text to convert to ASL.');
        return;
    }
    
    // Show generating in progress directly in the form
    const submitButton = textToVideoForm.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.innerHTML;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating Video...';
    submitButton.disabled = true;
    
    // Get form options
    const includeTransitions = document.getElementById('transitions-switch').checked;
    const resizeVideos = document.getElementById('resize-switch').checked;
    const detectHomonyms = document.getElementById('homonym-switch').checked;
    
    // Create form data
    const formData = new FormData();
    formData.append('text', textInput);
    formData.append('transitions', includeTransitions);
    formData.append('resize', resizeVideos);
    formData.append('detect_homonyms', detectHomonyms);
    
    try {
        const response = await fetch('/api/text-to-video', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        // Reset submit button
        submitButton.innerHTML = originalButtonText;
        submitButton.disabled = false;
        
        if (response.ok && data.status === 'success') {
            // Show result
            document.getElementById('text-to-video-result').classList.remove('d-none');
            
            // Display the video
            const videoElement = document.getElementById('generated-video');
            videoElement.src = data.video_url;
            videoElement.load();
            
            // Display the glossed text
            const glossedTextElement = document.getElementById('glossed-text');
            glossedTextElement.innerHTML = `<code>${data.glossed_text.join(' → ')}</code>`;
            
            // Display missing words if any
            const missingWordsDisplay = document.getElementById('missing-words-display');
            const missingWordsList = document.getElementById('missing-words-list');
            if (data.missing_words && data.missing_words.length > 0) {
                missingWordsDisplay.classList.remove('d-none');
                missingWordsList.textContent = data.missing_words.join(', ');
            } else {
                missingWordsDisplay.classList.add('d-none');
            }
            
            // Display homonym meanings if any were detected
            const homonymInfo = document.getElementById('homonym-info');
            const homonymMeanings = document.getElementById('homonym-meanings');
            
            // Always show homonym section if API key is available
            homonymInfo.classList.remove('d-none');
            
            // For debugging
            console.log("Homonym meanings:", data.homonym_meanings);
            
            // Create HTML for homonym meanings
            let homonymHTML = '<ul class="list-group list-group-flush">';
            
            // Add a default message if no homonym meanings
            if (!data.homonym_meanings || Object.keys(data.homonym_meanings).length === 0) {
                homonymHTML += `<li class="list-group-item">
                    <i>No homonym data available. API key may not be set.</i>
                </li>`;
            } else {
                // Always show the raw API response first
                if (data.homonym_meanings.hasOwnProperty('raw_response')) {
                    homonymHTML += `<li class="list-group-item py-2 px-3 bg-light">
                        <strong>Raw API Response:</strong><br>
                        <span class="font-monospace">${data.homonym_meanings.raw_response}</span>
                    </li>`;
                }
                
                // Process other homonym entries (excluding raw_response)
                // Group homonyms that have the same base word (e.g., "saw" and "saw_1")
                const groupedHomonyms = {};
                
                for (const [word, meaning] of Object.entries(data.homonym_meanings)) {
                    // Skip the raw_response entry
                    if (word === 'raw_response') continue;
                    
                    // Check if this is a duplicate homonym with a number suffix (e.g., "saw_1")
                    const baseWord = word.split('_')[0];
                    
                    if (!groupedHomonyms[baseWord]) {
                        groupedHomonyms[baseWord] = [];
                    }
                    
                    // Convert object to string if necessary
                    const meaningStr = typeof meaning === 'object' ? 
                        JSON.stringify(meaning) : String(meaning);
                    
                    groupedHomonyms[baseWord].push(meaningStr);
                }
                
                // Now display the grouped homonyms
                for (const [baseWord, meanings] of Object.entries(groupedHomonyms)) {
                    if (meanings.length === 1) {
                        // Single meaning
                        homonymHTML += `<li class="list-group-item py-1 px-2">
                            <strong>${baseWord}</strong>: ${meanings[0]}
                        </li>`;
                    } else {
                        // Multiple meanings for the same word
                        homonymHTML += `<li class="list-group-item py-1 px-2">
                            <strong>${baseWord}</strong>:
                            <ul class="mb-0 ps-4">
                                ${meanings.map(m => `<li>${m}</li>`).join('')}
                            </ul>
                        </li>`;
                    }
                }
            }
            
            homonymHTML += '</ul>';
            
            homonymMeanings.innerHTML = homonymHTML;
            
            // Scroll to result
            document.getElementById('text-to-video-result').scrollIntoView({behavior: 'smooth'});
        } else {
            showError(data.error || 'Failed to generate ASL video.');
        }
    } catch (error) {
        // Reset submit button
        submitButton.innerHTML = originalButtonText;
        submitButton.disabled = false;
        showError('Network error. Please try again.');
        console.error('Error:', error);
    }
}

/**
 * Handle video to text conversion
 */
async function handleVideoToText(event) {
    event.preventDefault();
    
    const videoInput = document.getElementById('video-input');
    if (!videoInput.files || videoInput.files.length === 0) {
        showError('Please select a video file.');
        return;
    }
    
    const file = videoInput.files[0];
    
    // Check file type
    const fileType = file.type;
    if (!fileType.startsWith('video/')) {
        showError('Please select a valid video file.');
        return;
    }
    
    // Show generating in progress directly in the form
    const submitButton = videoToTextForm.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.innerHTML;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing Video...';
    submitButton.disabled = true;
    
    // Create form data
    const formData = new FormData();
    formData.append('video', file);
    formData.append('top_k', document.getElementById('top-k').value);
    
    try {
        const response = await fetch('/api/video-to-text', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        // Reset submit button
        submitButton.innerHTML = originalButtonText;
        submitButton.disabled = false;
        
        if (response.ok && data.status === 'success') {
            // Show result
            document.getElementById('video-to-text-result').classList.remove('d-none');
            
            // Display the uploaded video
            const videoElement = document.getElementById('uploaded-video');
            videoElement.src = URL.createObjectURL(file);
            videoElement.load();
            
            // Display the recognition results
            displayRecognitionResults(data.predictions, 'recognition-results');
            
            // Scroll to result
            document.getElementById('video-to-text-result').scrollIntoView({behavior: 'smooth'});
        } else {
            showError(data.error || 'Failed to recognize signs.');
        }
    } catch (error) {
        // Reset submit button
        submitButton.innerHTML = originalButtonText;
        submitButton.disabled = false;
        showError('Network error. Please try again.');
        console.error('Error:', error);
    }
}

/**
 * Handle random video selection
 */
async function handleRandomVideo() {
    // Show loading in the button
    const submitButton = randomVideoBtn;
    const originalButtonText = submitButton.innerHTML;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading Random Video...';
    submitButton.disabled = true;
    
    // Get form options
    const recognize = document.getElementById('recognize-switch').checked;
    
    // Create form data
    const formData = new FormData();
    formData.append('recognize', recognize);
    
    try {
        const response = await fetch('/api/random-video', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        // Reset submit button
        submitButton.innerHTML = originalButtonText;
        submitButton.disabled = false;
        
        if (response.ok && data.status === 'success') {
            // Show result
            document.getElementById('random-video-result').classList.remove('d-none');
            
            // Display the random video
            const videoElement = document.getElementById('random-video-player');
            videoElement.src = data.video_url;
            videoElement.load();
            
            // Display the word
            document.getElementById('random-video-word').textContent = data.word;
            
            // Display recognition results if available
            const recognitionContainer = document.getElementById('random-recognition-container');
            if (recognize && data.predictions && data.predictions.length > 0) {
                recognitionContainer.classList.remove('d-none');
                displayRecognitionResults(data.predictions, 'random-recognition-results');
            } else {
                recognitionContainer.classList.add('d-none');
            }
            
            // Scroll to result
            document.getElementById('random-video-result').scrollIntoView({behavior: 'smooth'});
        } else {
            showError(data.error || 'Failed to get random video.');
        }
    } catch (error) {
        // Reset submit button
        submitButton.innerHTML = originalButtonText;
        submitButton.disabled = false;
        showError('Network error. Please try again.');
        console.error('Error:', error);
    }
}

/**
 * Display recognition results in a list
 */
function displayRecognitionResults(predictions, elementId) {
    const resultsElement = document.getElementById(elementId);
    resultsElement.innerHTML = '';
    
    predictions.forEach((pred, index) => {
        const confidence = (pred.confidence * 100).toFixed(2);
        const isTopResult = index === 0;
        
        const listItem = document.createElement('li');
        listItem.className = `list-group-item ${isTopResult ? 'list-group-item-success' : ''}`;
        
        const wordSpan = document.createElement('span');
        wordSpan.className = 'recognition-word';
        wordSpan.textContent = pred.word;
        
        const confidenceSpan = document.createElement('span');
        confidenceSpan.className = 'recognition-confidence';
        confidenceSpan.textContent = `${confidence}%`;
        
        const barContainer = document.createElement('div');
        barContainer.className = 'w-100 mt-2';
        
        const bar = document.createElement('div');
        bar.className = 'confidence-bar';
        bar.style.width = `${confidence}%`;
        
        barContainer.appendChild(bar);
        listItem.appendChild(wordSpan);
        listItem.appendChild(confidenceSpan);
        listItem.appendChild(barContainer);
        
        resultsElement.appendChild(listItem);
    });
}

/**
 * Show error modal with message
 */
function showError(message) {
    document.getElementById('error-message').textContent = message;
    errorModal.show();
}