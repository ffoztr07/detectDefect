const imageInput = document.getElementById('imageInput');
const preview = document.getElementById('preview');
const result = document.getElementById('result');
const previewContainer = document.getElementById('preview-container');

// Create fixed detect defect button
const detectDefectButton = document.createElement('button');
detectDefectButton.textContent = 'Detect Defect';
detectDefectButton.style.position = 'fixed';
detectDefectButton.style.bottom = '20px';
detectDefectButton.style.left = '50%';
detectDefectButton.style.transform = 'translateX(-50%)';
detectDefectButton.style.padding = '10px 20px';
detectDefectButton.style.backgroundColor = '#4CAF50';
detectDefectButton.style.color = 'white';
detectDefectButton.style.border = 'none';
detectDefectButton.style.borderRadius = '5px';
detectDefectButton.style.cursor = 'pointer';
detectDefectButton.style.display = 'none';
detectDefectButton.style.zIndex = '1000';
document.body.appendChild(detectDefectButton);

// Store the highest confidence apple detection
let highestConfidenceApple = null;

// Add camera button
const cameraButton = document.createElement('button');
cameraButton.textContent = 'Open Camera';
cameraButton.style.marginLeft = '10px';
imageInput.parentNode.insertBefore(cameraButton, imageInput.nextSibling);

// Function to handle camera input
async function handleCameraInput() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        const video = document.createElement('video');
        video.srcObject = stream;
        video.autoplay = true;
        video.style.width = '100%';
        video.style.maxWidth = '800px';
        video.style.height = 'auto';
        video.style.margin = '10px 0';
        
        // Create video container
        const videoContainer = document.createElement('div');
        videoContainer.style.textAlign = 'center';
        videoContainer.style.margin = '20px 0';
        videoContainer.appendChild(video);
        
        // Insert video container after the buttons
        cameraButton.parentNode.insertBefore(videoContainer, cameraButton.nextSibling);
        
        // Create canvas for capturing
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Create capture button
        const captureButton = document.createElement('button');
        captureButton.textContent = 'Take Photo';
        captureButton.style.marginLeft = '10px';
        cameraButton.parentNode.insertBefore(captureButton, cameraButton.nextSibling);
        
        // Start video
        await video.play();
        
        // Handle capture
        captureButton.onclick = () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0);
            
            // Convert canvas to blob
            canvas.toBlob((blob) => {
                const file = new File([blob], 'camera-photo.jpg', { type: 'image/jpeg' });
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                imageInput.files = dataTransfer.files;
                
                // Trigger the change event
                const event = new Event('change', { bubbles: true });
                imageInput.dispatchEvent(event);
                
                // Cleanup
                stream.getTracks().forEach(track => track.stop());
                videoContainer.remove();
                captureButton.remove();
            }, 'image/jpeg');
        };
    } catch (error) {
        alert('Error accessing camera: ' + error.message);
    }
}

// Add click handler for camera button
cameraButton.onclick = handleCameraInput;

// Function to crop and save image
async function cropAndSaveImage(img, box) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // Set canvas size to match the detection box
    canvas.width = box[2] - box[0];
    canvas.height = box[3] - box[1];
    
    // Draw the cropped portion
    ctx.drawImage(
        img,
        box[0], box[1], // Source x, y
        box[2] - box[0], box[3] - box[1], // Source width, height
        0, 0, // Destination x, y
        canvas.width, canvas.height // Destination width, height
    );
    
    // Convert canvas to blob
    const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
    
    // Create FormData and append the cropped image
    const formData = new FormData();
    formData.append('cropped_apple', blob, 'apple.png');

    try {
        // Send to backend
        const response = await fetch('/save_apple', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            result.innerHTML = `<h2>Prediction Result:</h2><p>${data.message}</p>`;
        } else {
            throw new Error('Failed to save apple image');
        }
    } catch (error) {
        alert('Error saving apple image: ' + error.message);
    }
}

imageInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Display the selected image
    preview.src = URL.createObjectURL(file);
    preview.onload = async () => {
        preview.style.display = 'block';
        // Create form data
        const formData = new FormData();
        formData.append('file', file);

        try {
            // Send the image to the API
            const response = await fetch('/detect', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();

            // Clear previous detection boxes
            const boxes = document.querySelectorAll('.detection-box');
            boxes.forEach(box => box.remove());

            // Display detection results
            result.innerHTML = '<h2>Detections:</h2>';
            
            // Find the apple detection with highest confidence
            highestConfidenceApple = null;
            data.detections.forEach(detection => {
                if (detection.class.toLowerCase() === 'apple') {
                    if (!highestConfidenceApple || detection.confidence > highestConfidenceApple.confidence) {
                        highestConfidenceApple = detection;
                    }
                }
            });

            // Show/hide detect defect button based on apple detection
            detectDefectButton.style.display = highestConfidenceApple ? 'block' : 'none';

            const containerWidth = 800;
            const containerHeight = 600;
            const imgWidth = preview.naturalWidth;
            const imgHeight = preview.naturalHeight;
            // Calculate scale and offset for object-fit: contain
            const scale = Math.min(containerWidth / imgWidth, containerHeight / imgHeight) * 1.2;
            const dispWidth = imgWidth * scale;
            const dispHeight = imgHeight * scale;
            const offsetX = (containerWidth - dispWidth) / 2;
            const offsetY = (containerHeight - dispHeight) / 2;

            // Display all detections
            data.detections.forEach(detection => {
                if (detection.class.toLowerCase() === 'apple') {
                    const box = document.createElement('div');
                    box.className = 'detection-box';
                    // Scale and offset box coordinates
                    const x1 = detection.box[0] * scale + offsetX;
                    const y1 = detection.box[1] * scale + offsetY;
                    const x2 = detection.box[2] * scale + offsetX;
                    const y2 = detection.box[3] * scale + offsetY;
                    box.style.left = `${x1}px`;
                    box.style.top = `${y1}px`;
                    box.style.width = `${x2 - x1}px`;
                    box.style.height = `${y2 - y1}px`;
                    
                    // Add label
                    const label = document.createElement('div');
                    label.textContent = `apple (${(detection.confidence * 100).toFixed(1)}%)`;
                    label.style.position = 'absolute';
                    label.style.top = '50%';
                    label.style.left = '50%';
                    label.style.transform = 'translate(-50%, -50%)';
                    label.style.color = 'white';
                    label.style.fontWeight = 'bold';
                    label.style.textShadow = '1px 1px 2px black';
                    label.style.pointerEvents = 'auto';
                    box.appendChild(label);
                    
                    previewContainer.appendChild(box);
                }

                result.innerHTML += `
                    <p>Class: ${detection.class}<br>
                    Confidence: ${(detection.confidence * 100).toFixed(2)}%</p>
                `;
            });
        } catch (error) {
            result.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
            detectDefectButton.style.display = 'none';
        }
    };
});

// Add click handler for the fixed detect defect button
detectDefectButton.onclick = () => {
    if (highestConfidenceApple) {
        cropAndSaveImage(preview, highestConfidenceApple.box);
    }
}; 