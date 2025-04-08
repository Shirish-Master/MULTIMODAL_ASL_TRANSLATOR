/**
 * ASL WLASL Converter Setup Page JavaScript
 * Handles setup page UI interactions and API calls
 */

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check setup status
    checkSetupStatus();
});

/**
 * Check and display setup status
 */
async function checkSetupStatus() {
    try {
        const response = await fetch('/api/setup-check');
        const data = await response.json();
        
        if (data.status === 'success') {
            updateSetupStatus(data);
            updatePaths(data);
        } else {
            showSetupError('Failed to check setup status.');
        }
    } catch (error) {
        showSetupError('Network error. Please try again.');
        console.error('Error:', error);
    }
}

/**
 * Update setup status display
 */
function updateSetupStatus(data) {
    const statusElement = document.getElementById('setup-status');
    let html = '';
    
    // Overall status
    if (data.json_exists && data.videos_dir_exists && data.video_count > 0) {
        statusElement.classList.remove('alert-info');
        statusElement.classList.add('alert-success');
        html += `<h5><i class="fas fa-check-circle me-2"></i>Dataset Ready</h5>`;
    } else {
        statusElement.classList.remove('alert-info');
        statusElement.classList.add('alert-warning');
        html += `<h5><i class="fas fa-exclamation-triangle me-2"></i>Setup Required</h5>`;
    }
    
    // Detailed status
    html += '<ul class="list-group mt-3">';
    
    // JSON metadata status
    if (data.json_exists) {
        html += `
            <li class="list-group-item list-group-item-success d-flex align-items-center">
                <span class="status-check"><i class="fas fa-check-circle"></i></span>
                <div>
                    <strong>WLASL Metadata</strong>
                    <div class="status-text">WLASL_v0.3.json is available at ${data.json_path}</div>
                </div>
            </li>
        `;
    } else {
        html += `
            <li class="list-group-item list-group-item-danger d-flex align-items-center">
                <span class="status-check"><i class="fas fa-times-circle"></i></span>
                <div>
                    <strong>WLASL Metadata Missing</strong>
                    <div class="status-text">WLASL_v0.3.json not found at ${data.json_path}</div>
                </div>
            </li>
        `;
    }
    
    // Videos directory status
    if (data.videos_dir_exists) {
        html += `
            <li class="list-group-item list-group-item-success d-flex align-items-center">
                <span class="status-check"><i class="fas fa-check-circle"></i></span>
                <div>
                    <strong>Videos Directory</strong>
                    <div class="status-text">Videos directory exists at ${data.videos_dir}</div>
                </div>
            </li>
        `;
    } else {
        html += `
            <li class="list-group-item list-group-item-danger d-flex align-items-center">
                <span class="status-check"><i class="fas fa-times-circle"></i></span>
                <div>
                    <strong>Videos Directory Missing</strong>
                    <div class="status-text">Videos directory not found at ${data.videos_dir}</div>
                </div>
            </li>
        `;
    }
    
    // Video files status
    if (data.videos_dir_exists) {
        if (data.video_count > 0) {
            html += `
                <li class="list-group-item list-group-item-success d-flex align-items-center">
                    <span class="status-check"><i class="fas fa-check-circle"></i></span>
                    <div>
                        <strong>Video Files</strong>
                        <div class="status-text">Found ${data.video_count} video files</div>
                    </div>
                </li>
            `;
        } else {
            html += `
                <li class="list-group-item list-group-item-warning d-flex align-items-center">
                    <span class="status-check"><i class="fas fa-exclamation-triangle"></i></span>
                    <div>
                        <strong>No Video Files</strong>
                        <div class="status-text">No video files found in the videos directory</div>
                    </div>
                </li>
            `;
        }
    }
    
    // Model status
    if (data.model_exists) {
        html += `
            <li class="list-group-item list-group-item-success d-flex align-items-center">
                <span class="status-check"><i class="fas fa-check-circle"></i></span>
                <div>
                    <strong>Pretrained Model</strong>
                    <div class="status-text">I3D model is available at ${data.model_path}</div>
                </div>
            </li>
        `;
    } else {
        html += `
            <li class="list-group-item list-group-item-warning d-flex align-items-center">
                <span class="status-check"><i class="fas fa-exclamation-triangle"></i></span>
                <div>
                    <strong>Pretrained Model Missing</strong>
                    <div class="status-text">I3D model not found at ${data.model_path}</div>
                    <div class="small mt-1">Note: The model is only required for video-to-text recognition</div>
                </div>
            </li>
        `;
    }
    
    html += '</ul>';
    
    statusElement.innerHTML = html;
}

/**
 * Update path displays
 */
function updatePaths(data) {
    document.getElementById('data-dir-path').textContent = data.json_path.replace('/WLASL_v0.3.json', '');
    document.getElementById('videos-dir-path').textContent = data.videos_dir;
    document.getElementById('models-dir-path').textContent = data.model_path.replace('/i3d_model.pth', '');
}

/**
 * Show setup error
 */
function showSetupError(message) {
    const statusElement = document.getElementById('setup-status');
    statusElement.classList.remove('alert-info');
    statusElement.classList.add('alert-danger');
    statusElement.innerHTML = `<h5><i class="fas fa-times-circle me-2"></i>Error</h5><p>${message}</p>`;
}